import logging
import os
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

FREEPIK_API_BASE = "https://api.freepik.com/v1"


class FreepikService:
    """
    Service for searching images on Freepik.
    Requires FREEPIK_API_KEY environment variable or api_key parameter.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 10
    ):
        self.api_key = api_key or os.getenv('FREEPIK_API_KEY')
        if not self.api_key:
            raise ValueError("Freepik API key is required. Set FREEPIK_API_KEY environment variable or pass api_key parameter.")
        self.timeout = timeout
        self.headers = {
            'x-freepik-api-key': self.api_key
        }
    
    def search_images_by_phrases_list(
        self,
        search_phrases: List[str],
        limit: int = 15,
        orientation: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search Freepik for images based on keywords.
        Args:
            search_phrases: List of search phrases to search for
            limit: Maximum number of results per search phrase (default: 15)
        Returns:
            List of dictionaries containing image information:
            - title: Unique identifier with Freepik ID and title
            - description: Resource title (same as title)
            - image_url: Direct URL to the image
            - dimensions: Image dimensions as "WxH" string
            - timestamp: Publication date if available
        """
        fetched_images = []

        for search_phrase in search_phrases:
            try:
                params = {
                    'term': search_phrase,
                    'limit': limit,
                    'filters[content_type][photo]': 1,  # Only fetch photos
                    'filters[license][freemium]': 1,  # Only free images
                }
                
                if orientation and orientation in ['landscape', 'panoramic']:
                    params['filters[orientation][landscape]'] = 1
                    params['filters[orientation][panoramic]'] = 1
                
                response = requests.get(
                    f"{FREEPIK_API_BASE}/resources",
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                resources = data.get('data', [])
                
                if not resources:
                    continue
                
                for resource in resources:
                    resource_id = resource.get('id')
                    title = resource.get('title', '')
                    image = resource.get('image', {})
                    source = image.get('source', {})
                    image_url = source.get('url')
                    size = source.get('size', '')  # Format: "WxH"
                    
                    # Get publication timestamp
                    meta = resource.get('meta', {})
                    published_at = meta.get('published_at')

                    if resource_id and image_url:
                        fetched_images.append({
                            'title': f"{resource_id}_{title}",
                            'description': title if title else None,
                            'image_url': image_url,
                            'dimensions': size if size else None,
                            'timestamp': published_at
                        })
                
            except requests.RequestException as exc:
                logger.error(f"Error querying Freepik API: {exc}")
            except Exception as exc:
                logger.error(f"Unexpected error finding image on Freepik: {exc}")

        return fetched_images
