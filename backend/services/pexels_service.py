import logging
import os
import time
import requests
from typing import List, Dict, Any, Optional

from services.redis_client import get_redis_client

logger = logging.getLogger(__name__)

PEXELS_API_BASE = "https://api.pexels.com/v1"
PEXELS_RATE_LIMIT_CACHE_KEY = "pexels:rate_limit_until"

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
        self._redis_client = None
    
    def _get_redis(self):
        """Lazy-load Redis client."""
        if self._redis_client is None:
            self._redis_client = get_redis_client()
        return self._redis_client
    
    def is_rate_limited(self) -> bool:
        """
        Check if the Pexels API is currently rate limited.
        Returns True if rate limited, False otherwise.
        """
        try:
            redis_client = self._get_redis()
            return redis_client.exists(PEXELS_RATE_LIMIT_CACHE_KEY) > 0  # If the key exists, we're still rate limited (TTL handles expiration)
        except Exception as exc:
            logger.warning(f"Failed to check rate limit status in Redis: {exc}")
            return False  # Fail open - allow API calls if Redis is unavailable
    
    def _set_rate_limit_until(self, reset_timestamp: int) -> None:
        """
        Store the rate limit in Redis with TTL based on the reset timestamp.
        The key will automatically expire when the rate limit window ends.
        """
        try:
            redis_client = self._get_redis()
            ttl_seconds = max(1, reset_timestamp - int(time.time()))
            redis_client.setex(
                PEXELS_RATE_LIMIT_CACHE_KEY,
                ttl_seconds,
                "1"  # Value doesn't matter, we only check existence
            )
            logger.warning(f"Pexels API rate limit set until {reset_timestamp} ({ttl_seconds} seconds from now)")
        except Exception as exc:
            logger.error(f"Failed to set rate limit in Redis: {exc}")
    
    def get_rate_limit_remaining_seconds(self) -> int:
        """
        Get the remaining seconds until the rate limit expires.
        Returns 0 if not rate limited.
        """
        try:
            redis_client = self._get_redis()
            ttl = redis_client.ttl(PEXELS_RATE_LIMIT_CACHE_KEY)
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
        
        # Check if we're currently rate limited
        if self.is_rate_limited():
            remaining = self.get_rate_limit_remaining_seconds()
            logger.info(f"Pexels API is rate limited. Skipping API calls. Rate limit expires in {remaining} seconds.")
            return []
        
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
                
                # Handle rate limit response (HTTP 429)
                if response.status_code == 429:
                    # Pexels doesn't include rate limit headers on 429, use a default of 1 hour
                    reset_timestamp = int(time.time()) + 3600
                    self._set_rate_limit_until(reset_timestamp)
                    logger.warning(f"Pexels API rate limit hit. Will retry after 1 hour.")
                    return fetched_images  # Return whatever we've collected so far
                
                response.raise_for_status()
                
                # Track rate limit from response headers on successful requests
                reset_header = response.headers.get('X-Ratelimit-Reset')
                remaining_header = response.headers.get('X-Ratelimit-Remaining')
                if reset_header and remaining_header:
                    try:
                        remaining = int(remaining_header)
                        if remaining <= 0:
                            # We've exhausted our quota, set rate limit until reset
                            reset_timestamp = int(reset_header)
                            self._set_rate_limit_until(reset_timestamp)
                            logger.warning(f"Pexels API quota exhausted. Rate limit set until reset.")
                            return fetched_images
                    except ValueError:
                        logger.warning(f"Invalid rate limit headers: Reset={reset_header}, Remaining={remaining_header}")
                
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
