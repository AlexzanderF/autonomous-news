import logging
import os
import requests
from typing import List, Dict, Any, Optional

from services.redis_client import get_redis_client

logger = logging.getLogger(__name__)

FREEPIK_API_BASE = "https://api.freepik.com/v1"
FREEPIK_RATE_LIMIT_CACHE_KEY = "freepik:rate_limit_until"
DEFAULT_RATE_LIMIT_SECONDS = 60  # Default wait time if Retry-After header is missing


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
        self._redis_client = None
    
    def _get_redis(self):
        """Lazy-load Redis client."""
        if self._redis_client is None:
            self._redis_client = get_redis_client()
        return self._redis_client
    
    def is_rate_limited(self) -> bool:
        """
        Check if the Freepik API is currently rate limited.
        Returns True if rate limited, False otherwise.
        """
        try:
            redis_client = self._get_redis()
            return redis_client.exists(FREEPIK_RATE_LIMIT_CACHE_KEY) > 0  # If the key exists, we're still rate limited (TTL handles expiration)
        except Exception as exc:
            logger.warning(f"Failed to check rate limit status in Redis: {exc}")
            return False  # Fail open - allow API calls if Redis is unavailable
    
    def _set_rate_limit(self, retry_after_seconds: int) -> None:
        """
        Store the rate limit in Redis with TTL set to retry_after_seconds.
        The key will automatically expire when the rate limit window ends.
        """
        try:
            redis_client = self._get_redis()
            redis_client.setex(
                FREEPIK_RATE_LIMIT_CACHE_KEY,
                retry_after_seconds,
                "1"  # Value doesn't matter, we only check existence
            )
            logger.warning(f"Freepik API rate limit set for {retry_after_seconds} seconds")
        except Exception as exc:
            logger.error(f"Failed to set rate limit in Redis: {exc}")
    
    def get_rate_limit_remaining_seconds(self) -> int:
        """
        Get the remaining seconds until the rate limit expires.
        Returns 0 if not rate limited.
        """
        try:
            redis_client = self._get_redis()
            ttl = redis_client.ttl(FREEPIK_RATE_LIMIT_CACHE_KEY)
            return max(0, ttl)
        except Exception as exc:
            logger.warning(f"Failed to get rate limit TTL from Redis: {exc}")
            return 0
    
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
        
        # Check if we're currently rate limited
        if self.is_rate_limited():
            remaining = self.get_rate_limit_remaining_seconds()
            logger.info(f"Freepik API is rate limited. Skipping API calls. Rate limit expires in {remaining} seconds.")
            return []
        
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
                
                # Handle rate limit response (HTTP 429)
                if response.status_code == 429:
                    retry_after = DEFAULT_RATE_LIMIT_SECONDS
                    retry_after_header = response.headers.get('Retry-After')
                    if retry_after_header:
                        try:
                            retry_after = int(retry_after_header)
                        except ValueError:
                            logger.warning(f"Invalid Retry-After header value: {retry_after_header}")
                    
                    self._set_rate_limit(retry_after)
                    logger.warning(f"Freepik API rate limit hit. Will retry after {retry_after} seconds.")
                    return fetched_images  # Return whatever we've collected so far
                
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
