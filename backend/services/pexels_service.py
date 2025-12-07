import logging
import os
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

PEXELS_API_BASE = "https://api.pexels.com/v1"

# Pexels API configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

class PexelsService:
    """
    Service for searching images on Pexels.
    Requires PEXELS_API_KEY environment variable or api_key parameter.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 10
    ):
        self.api_key = api_key or PEXELS_API_KEY
        if not self.api_key:
            raise ValueError("Pexels API key is required. Set PEXELS_API_KEY environment variable or pass api_key parameter.")
        self.timeout = timeout
        self.headers = {
            'Authorization': self.api_key
        }
    
    def search_images_by_phrases_list(
        self,
        search_phrases: List[str],
        limit: int = 15,
        orientation: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search Pexels for images based on keywords.
        Args:
            search_phrases: List of search phrases to search for
            limit: Maximum number of results per search phrase (default: 15)
            orientation: Image orientation (default: None)
        Returns:
            List of dictionaries containing image information:
            - title: Unique identifier
            - description: Photo alt text
            - image_url: Direct URL to the original image
            - dimensions: Image dimensions as "WxH" string
            - timestamp: None (not available from Pexels)
        """
        fetched_images = []

        for search_phrase in search_phrases:
            try:
                params = {
                    'query': search_phrase,
                    'per_page': limit,
                }
                
                if orientation:
                    params['orientation'] = orientation
                
                response = requests.get(
                    f"{PEXELS_API_BASE}/search",
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                photos = data.get('photos', [])
                
                if not photos:
                    continue
                
                for photo in photos:
                    photo_id = photo.get('id')
                    alt_text = photo.get('alt', '')
                    src = photo.get('src', {})
                    image_url = src.get('original')
                    width = photo.get('width')
                    height = photo.get('height')

                    if photo_id and image_url:
                        fetched_images.append({
                            'title': f"{photo_id}_{alt_text}",
                            'description': alt_text if alt_text else None,
                            'image_url': image_url,
                            'dimensions': f"{width}x{height}" if width and height else None,
                            'timestamp': None
                        })
                
            except requests.RequestException as exc:
                logger.error(f"Error querying Pexels API: {exc}")
            except Exception as exc:
                logger.error(f"Unexpected error finding image on Pexels: {exc}")

        return fetched_images
