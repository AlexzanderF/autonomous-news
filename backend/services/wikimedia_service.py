import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

WIKIMEDIA_API_BASE = "https://commons.wikimedia.org/w/api.php"
WIKIMEDIA_IMAGE_URL_TEMPLATE = "https://commons.wikimedia.org/wiki/Special:FilePath/{filename}"
WIKIMEDIA_HEADERS = {
    'User-Agent': (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/svg+xml',
    'image/svg'
}
DESCRIPTION_MAX_LENGTH = 500
THUMBNAIL_MAX_WIDTH = 1280  # 16:9 at 720p resolution


class WikimediaService:

    def __init__(
        self,
        api_base: str = WIKIMEDIA_API_BASE,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10
    ):
        self.api_base = api_base
        self.headers = headers or WIKIMEDIA_HEADERS
        self.timeout = timeout
    
    def search_images_by_phrases_list(
        self,
        search_phrases: List[str],
        limit: int = 20,
        namespace: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Search Wikimedia Commons for images based on keywords.
        Args:
            search_phrases: List of search phrases to search for
            limit: Maximum number of results per search phrase (default: 20)
            namespace: Wikimedia namespace to search in (default: 6 for files/media)
        Returns:
            List of dictionaries containing image information:
            - title: The file title on Wikimedia
            - description: Image description if available
            - image_url: Direct URL to the image
            - dimensions: Image dimensions as "WxH" string if available
            - timestamp: Upload timestamp (ISO format) if available
        """
        fetched_images = []

        for search_phrase in search_phrases:
            try:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'generator': 'search',
                    'gsrsearch': f"{search_phrase} filetype:bitmap",
                    'gsrnamespace': namespace,
                    'gsrlimit': limit,
                    'prop': 'imageinfo',
                    'iiprop': 'url|mime|size|mediatype|extmetadata|timestamp|thumbmime',
                    'iiurlwidth': THUMBNAIL_MAX_WIDTH
                }
                
                response = requests.get(
                    self.api_base, 
                    params=params, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if 'query' not in data or 'pages' not in data['query']:
                    continue
                
                search_results = data['query']['pages'].values()
                
                if not search_results:
                    continue
                
                for result in search_results:
                    title = result.get('title')
                    image_info = result.get('imageinfo', [{}])[0]
                    
                    if image_info.get('mime') not in ALLOWED_MIME_TYPES:
                        continue

                    # Original image URL and dimensions
                    original_url = image_info.get('url')
                    original_width = image_info.get('width')
                    original_height = image_info.get('height')
                    
                    # Thumbnail URL (scaled to max THUMBNAIL_MAX_WIDTH via iiurlwidth parameter)
                    thumb_url = image_info.get('thumburl')
                    thumb_width = image_info.get('thumbwidth')
                    thumb_height = image_info.get('thumbheight')
                    
                    # Always prefer thumbnail when available (capped at THUMBNAIL_MAX_WIDTH)
                    # Thumbnail is only generated when original is larger than requested width
                    if thumb_url:
                        image_url = thumb_url
                        width = thumb_width
                        height = thumb_height
                        logger.debug(f"Using thumbnail ({thumb_width}x{thumb_height}) instead of original ({original_width}x{original_height}) for: {title}")
                    else:
                        # No thumbnail means original is already <= THUMBNAIL_MAX_WIDTH, use it directly
                        image_url = original_url
                        width = original_width
                        height = original_height
                        logger.debug(f"Using original image ({original_width}x{original_height}), no thumbnail needed for: {title}")
                    
                    description = image_info.get('extmetadata', {}).get('ImageDescription', {}).get('value')
                    if description and len(description) > DESCRIPTION_MAX_LENGTH:
                        description = description[:DESCRIPTION_MAX_LENGTH] + '...'

                    timestamp = image_info.get('timestamp')

                    if title and image_url: 
                        fetched_images.append({
                            'title': title,
                            'description': description if description else None,
                            'image_url': image_url,
                            'dimensions': f"{width}x{height}" if width and height else None,
                            'timestamp': timestamp
                        })
                
            except requests.RequestException as exc:
                logger.error(f"Error querying Wikimedia Commons API: {exc}")
            except Exception as exc:
                logger.error(f"Unexpected error finding image: {exc}")

        return fetched_images
    
    def get_image_url(self, filename: str) -> str:
        """
        Generate a direct URL to a Wikimedia Commons image.
        Args:
            filename: The filename on Wikimedia Commons
        Returns:
            Direct URL to the image file
        """
        return WIKIMEDIA_IMAGE_URL_TEMPLATE.format(filename=filename)
