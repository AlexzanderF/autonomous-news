"""
Image Storage Service

Downloads images from external providers and stores them locally on the VM.
Provides self-hosted URLs to avoid rate limiting from image providers.
"""

import os
import logging
import hashlib
import time
import requests
from io import BytesIO
from pathlib import Path
from typing import Optional
from PIL import Image
from services.image_constants import THUMBNAIL_MAX_WIDTH, AVIF_QUALITY

logger = logging.getLogger(__name__)

# Default storage path - can be overridden via environment variable
STORAGE_PATH = os.environ.get("THUMBNAIL_STORAGE_PATH", "/data/thumbnails")

# Supported image extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

# Request timeout for downloading images
DOWNLOAD_TIMEOUT = 30

# Retry configuration for rate limiting (429 errors)
MAX_RETRIES = int(os.environ.get("THUMBNAIL_DOWNLOAD_MAX_RETRIES", 0))
INITIAL_RETRY_DELAY = 10.0  # Wikimedia recommends longer waits for 429
RETRY_BACKOFF_MULTIPLIER = 2.0


class ImageStorageService:
    """
    Service for downloading and storing images locally.
    Images are resized if larger than THUMBNAIL_MAX_WIDTH and converted to AVIF format.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or STORAGE_PATH)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """Create the storage directory if it doesn't exist."""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Image storage directory ensured: {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to create storage directory {self.storage_path}: {e}")
            raise
    
    def _generate_filename(self, article_id: int, original_url: str, extension: str) -> str:
        """Generate a unique filename based on article ID, URL hash, and given extension."""
        # Create a short hash of the URL for uniqueness
        url_hash = hashlib.md5(original_url.encode()).hexdigest()[:12]
        return f"article_{article_id}_{url_hash}.{extension}"
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image if width exceeds THUMBNAIL_MAX_WIDTH, maintaining aspect ratio.
        """
        if image.width > THUMBNAIL_MAX_WIDTH:
            ratio = THUMBNAIL_MAX_WIDTH / image.width
            new_height = int(image.height * ratio)
            logger.info(f"Resizing image from {image.width}x{image.height} to {THUMBNAIL_MAX_WIDTH}x{new_height}")
            return image.resize((THUMBNAIL_MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
        return image
    
    def _convert_to_avif(self, image: Image.Image) -> bytes:
        """
        Convert image to AVIF format with compression.
        """
        # Convert to RGB if necessary (AVIF doesn't support all modes)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        output = BytesIO()
        image.save(output, format='AVIF', quality=AVIF_QUALITY)
        return output.getvalue()
    
    def _download_with_retry(self, url: str) -> requests.Response:
        """
        Download a URL with retry logic for 429 rate limit errors.
        Uses exponential backoff between retries.
        
        Args:
            url: The URL to download
            
        Returns:
            Response object from successful request
            
        Raises:
            requests.HTTPError: If all retries are exhausted or non-429 error occurs
        """
        headers = {
            'User-Agent': 'pyWikiCommons/1.1 (https://github.com/amckenna41/pyWikiCommons; afarkov@proton.me)',
        }
        
        delay = INITIAL_RETRY_DELAY
        
        # Use a session to persist cookies (Wikimedia sets WMF-Uniq cookie)
        session = requests.Session()
        session.headers.update(headers)
        
        for attempt in range(MAX_RETRIES + 1):
            response = session.get(
                url,
                timeout=DOWNLOAD_TIMEOUT,
                stream=True
            )
            
            if response.status_code == 429:
                if attempt < MAX_RETRIES:
                    logger.warning(
                        f"Rate limit (429) on attempt {attempt + 1}/{MAX_RETRIES + 1}, "
                        f"retrying in {delay:.1f}s: {url}"
                    )
                    time.sleep(delay)
                    delay *= RETRY_BACKOFF_MULTIPLIER
                    continue
                else:
                    logger.error(f"Rate limit (429) - all {MAX_RETRIES + 1} attempts exhausted: {url}")
                    response.raise_for_status()
            
            response.raise_for_status()
            return response
        
        # Should not reach here, but just in case
        raise requests.RequestException("Unexpected error in retry logic")

    def download_and_store(
        self, 
        article_id: int, 
        image_url: str, 
        fallback_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Download an image from the given URL and store it locally.
        If download fails with 429 and a fallback_url is provided, tries the fallback.
        
        Args:
            article_id: The article ID this image belongs to
            image_url: The URL of the image to download (typically thumbnail)
            fallback_url: Optional fallback URL to try if primary fails with 429
            
        Returns:
            The filename of the stored image (e.g., 'article_123_abc.jpg'), 
            or None if download failed. Frontend constructs full URL.
        """
        urls_to_try = [image_url]
        if fallback_url and fallback_url != image_url:
            urls_to_try.append(fallback_url)
        
        response = None
        
        for i, url in enumerate(urls_to_try):
            is_fallback = i > 0
            try:
                if is_fallback:
                    logger.info(f"Article {article_id}: trying fallback URL: {url}")
                else:
                    logger.info(f"Article {article_id}: downloading image: {url}")
                
                response = self._download_with_retry(url)
                break  # Success, exit the loop
                
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    if i < len(urls_to_try) - 1:
                        logger.warning(f"Article {article_id}: 429 on thumbnail, will try original URL")
                        continue
                    else:
                        logger.error(f"Article {article_id}: all URLs exhausted with 429 errors")
                        return None
                else:
                    logger.error(f"Article {article_id}: HTTP error {e.response.status_code if e.response else 'unknown'}: {url}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Article {article_id}: download failed: {e}")
                if i < len(urls_to_try) - 1:
                    continue  # Try next URL on network errors too
                return None
        
        if response is None:
            return None
        
        raw_data = response.content
        content_type = response.headers.get('Content-Type', '')
        
        try:
            # Load image data into memory for processing
            image_data = BytesIO(raw_data)
            image = Image.open(image_data)
            original_size = f"{image.width}x{image.height}"
            
            # Resize if necessary
            image = self._resize_image(image)
            
            # Convert to AVIF
            avif_data = self._convert_to_avif(image)
            
            # Generate filename
            filename = self._generate_filename(article_id, image_url, 'avif')
            file_path = self.storage_path / filename
            
            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(avif_data)
            
            file_size = file_path.stat().st_size
            logger.info(
                f"Article {article_id}: saved {filename} "
                f"(original: {original_size}, final: {image.width}x{image.height}, size: {file_size} bytes)"
            )
            
            # Return just the filename - frontend will construct the full URL
            return filename
            
        except Exception as e:
            # Fallback: save original image as-is if processing fails
            logger.warning(f"Article {article_id}: image processing failed ({e}), saving original")
            
            try:
                # Determine extension from content-type or URL
                extension = self._get_extension_from_content_type(content_type, image_url)
                filename = self._generate_filename(article_id, image_url, extension)
                file_path = self.storage_path / filename
                
                with open(file_path, 'wb') as f:
                    f.write(raw_data)
                
                file_size = file_path.stat().st_size
                logger.info(f"Article {article_id}: saved original as {filename} ({file_size} bytes)")
                return filename
                
            except Exception as fallback_error:
                logger.error(f"Article {article_id}: fallback save also failed: {fallback_error}")
                return None
    
    def _get_extension_from_content_type(self, content_type: str, url: str) -> str:
        """Get file extension from content-type header or URL, without leading dot."""
        # Try content-type first
        type_to_ext = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp',
            'image/svg+xml': 'svg',
            'image/avif': 'avif',
        }
        mime = content_type.split(';')[0].strip().lower()
        if mime in type_to_ext:
            return type_to_ext[mime]
        
        # Fallback to URL extension
        url_lower = url.lower()
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'avif']:
            if url_lower.endswith(f'.{ext}'):
                return 'jpg' if ext == 'jpeg' else ext
        
        return 'jpg'  # Ultimate fallback
    
    def get_image_path(self, filename: str) -> Optional[Path]:
        """
        Get the full path to a stored image.
        
        Args:
            filename: The filename of the stored image
            
        Returns:
            Path object if file exists, None otherwise
        """
        file_path = self.storage_path / filename
        if file_path.exists() and file_path.is_file():
            return file_path
        return None
    
    def delete_image(self, filename: str) -> bool:
        """
        Delete a stored image.
        
        Args:
            filename: The filename of the image to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = self.storage_path / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted image: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete image {filename}: {e}")
            return False


# Singleton instance for convenience
_default_service: Optional[ImageStorageService] = None


def get_image_storage_service() -> ImageStorageService:
    """Get the default ImageStorageService instance."""
    global _default_service
    if _default_service is None:
        _default_service = ImageStorageService()
    return _default_service
