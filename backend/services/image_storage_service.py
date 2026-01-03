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
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import mimetypes

logger = logging.getLogger(__name__)

# Default storage path - can be overridden via environment variable
STORAGE_PATH = os.environ.get("THUMBNAIL_STORAGE_PATH", "/data/thumbnails")

# Supported image extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

# Request timeout for downloading images
DOWNLOAD_TIMEOUT = 30

# Retry configuration for rate limiting (429 errors)
MAX_RETRIES = 2
INITIAL_RETRY_DELAY = 10.0  # Wikimedia recommends longer waits for 429
RETRY_BACKOFF_MULTIPLIER = 2.0


class ImageStorageService:
    """
    Service for downloading and storing images locally.
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
    
    def _generate_filename(self, article_id: int, original_url: str) -> str:
        """
        Generate a unique filename for the image based on article ID and URL hash.
        
        Args:
            article_id: The article ID this image belongs to
            original_url: The original URL of the image
            
        Returns:
            A filename like 'article_123_abc123def.jpg'
        """
        # Extract extension from URL or default to .jpg
        parsed = urlparse(original_url)
        path = parsed.path.lower()
        
        extension = '.jpg'  # Default
        for ext in SUPPORTED_EXTENSIONS:
            if path.endswith(ext):
                extension = ext
                break
        
        # Create a short hash of the URL for uniqueness
        url_hash = hashlib.md5(original_url.encode()).hexdigest()[:12]
        
        return f"article_{article_id}_{url_hash}{extension}"
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from Content-Type header."""
        extension = mimetypes.guess_extension(content_type.split(';')[0].strip())
        if extension in SUPPORTED_EXTENSIONS or (extension and extension.lstrip('.') in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}):
            return extension
        return '.jpg'  # Default fallback
    
    def _download_with_retry(self, url: str, context: str = "") -> requests.Response:
        """
        Download a URL with retry logic for 429 rate limit errors.
        Uses exponential backoff between retries.
        
        Args:
            url: The URL to download
            context: Optional context string for logging (e.g., "article 123")
            
        Returns:
            Response object from successful request
            
        Raises:
            requests.HTTPError: If all retries are exhausted or non-429 error occurs
        """
        # Use browser-like headers matching actual Chrome request
        # Wikimedia uses WMF-Uniq cookie to identify legitimate users, so use a session
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Ch-Ua': '"Chromium";v="120", "Google Chrome";v="120", "Not A(Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
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
                        f"Rate limit (429) downloading {context} "
                        f"on attempt {attempt + 1}/{MAX_RETRIES + 1}. Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= RETRY_BACKOFF_MULTIPLIER
                    continue
                else:
                    logger.error(
                        f"Rate limit (429) downloading {context} - "
                        f"all {MAX_RETRIES + 1} attempts exhausted"
                    )
                    response.raise_for_status()
            
            response.raise_for_status()
            return response
        
        # Should not reach here, but just in case
        raise requests.RequestException("Unexpected error in retry logic")
    
    def download_and_store(self, article_id: int, image_url: str) -> Optional[str]:
        """
        Download an image from the given URL and store it locally.
        
        Args:
            article_id: The article ID this image belongs to
            image_url: The URL of the image to download
            
        Returns:
            The filename of the stored image (e.g., 'article_123_abc.jpg'), 
            or None if download failed. Frontend constructs full URL.
        """
        try:
            logger.info(f"Downloading image for article {article_id}: {image_url}")
            
            # For Wikimedia URLs, add ?download= param to signal intentional download
            # This may help with CDN rate limiting vs hotlinking detection
            download_url = image_url
            if 'wikimedia.org' in image_url or 'wikipedia.org' in image_url:
                separator = '&' if '?' in image_url else '?'
                download_url = f"{image_url}{separator}download="
            
            response = self._download_with_retry(download_url, f"image for article {article_id}")
            
            # Verify we got an image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"Response is not an image (Content-Type: {content_type})")
                # Continue anyway, some servers don't set correct content-type
            
            # Generate filename (might update extension based on content-type)
            filename = self._generate_filename(article_id, image_url)
            
            # Update extension if content-type provides better info
            if content_type.startswith('image/'):
                new_ext = self._get_extension_from_content_type(content_type)
                if new_ext:
                    base_name = filename.rsplit('.', 1)[0]
                    filename = f"{base_name}{new_ext}"
            
            # Save to disk
            file_path = self.storage_path / filename
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = file_path.stat().st_size
            logger.info(f"Successfully saved image: {file_path} ({file_size} bytes)")
            
            # Return just the filename - frontend will construct the full URL
            return filename
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            return None
        except IOError as e:
            logger.error(f"Failed to save image for article {article_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error storing image for article {article_id}: {e}")
            return None
    
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
