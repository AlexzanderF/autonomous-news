"""
Proxy Service for handling rate-limited requests.

Uses DataImpulse residential proxy service for bypassing IP-based rate limits,
specifically for Wikimedia which blocks on IP level (unlike Pexels/Freepik which use API keys).
"""

import os
import logging
import requests
import uuid
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# DataImpulse Residential Proxy Configuration
# Credentials are loaded from environment variables for security
PROXY_HOST = os.environ.get("DATAIMPULSE_PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("DATAIMPULSE_PROXY_PORT", "823")
PROXY_USERNAME = os.environ.get("DATAIMPULSE_PROXY_USERNAME", "")
PROXY_PASSWORD = os.environ.get("DATAIMPULSE_PROXY_PASSWORD", "")

# Request timeout for proxied requests (may be slower than direct)
PROXY_REQUEST_TIMEOUT = 60
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
}

class ProxyService:
    """
    Service for making HTTP requests through a residential proxy.
    Used as a fallback when direct requests hit rate limits (429 errors).
    Uses session rotation to get a fresh IP for each request.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.host = host or PROXY_HOST
        self.port = port or PROXY_PORT
        self.username = username or PROXY_USERNAME
        self.password = password or PROXY_PASSWORD
    
    def is_configured(self) -> bool:
        """Check if the proxy service has valid credentials configured."""
        return bool(self.username and self.password)
    
    def _get_session_username(self) -> str:
        """
        Generate a username with a unique session ID for IP rotation.
        DataImpulse format: username__sessid.{random_id}
        """
        session_id = uuid.uuid4().hex[:8]
        return f"{self.username}__sessid.{session_id}"
    
    def _get_proxies(self, rotate_session: bool = True) -> Optional[Dict[str, str]]:
        """
        Get the proxy configuration dict for requests.
        
        Args:
            rotate_session: If True, use a new session ID for a fresh IP
        """
        if not self.username or not self.password:
            return None
        
        username = self._get_session_username() if rotate_session else self.username
        proxy_url = f"http://{username}:{self.password}@{self.host}:{self.port}"
        
        return {
            "http": proxy_url,
            "https": proxy_url,
        }
    
    def get_with_proxy(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = PROXY_REQUEST_TIMEOUT,
        stream: bool = True,
    ) -> requests.Response:
        """
        Make a GET request through the residential proxy with a fresh IP.
        Uses realistic browser headers to avoid detection.
        
        Args:
            url: The URL to request
            headers: Optional headers to include (will override defaults)
            timeout: Request timeout in seconds
            stream: Whether to stream the response
            
        Returns:
            requests.Response object
            
        Raises:
            ValueError: If proxy is not configured
            requests.RequestException: On request failure
        """
        if not self.is_configured():
            raise ValueError("Proxy service is not configured. Set DATAIMPULSE_PROXY_* environment variables.")
        
        proxies = self._get_proxies(rotate_session=True)
        
        browser_headers = DEFAULT_HEADERS
        
        # Override with custom headers if provided
        if headers:
            browser_headers.update(headers)
        
        logger.info(f"Making proxied request (new session) to: {url}")
        
        response = requests.get(
            url,
            headers=browser_headers,
            proxies=proxies,
            timeout=timeout,
            stream=stream,
            verify=True,
        )
        
        logger.info(f"Proxied request completed with status: {response.status_code}")
        
        return response


# Singleton instance for convenience
_default_service: Optional[ProxyService] = None

def get_proxy_service() -> ProxyService:
    """Get the default ProxyService instance."""
    global _default_service
    if _default_service is None:
        _default_service = ProxyService()
    return _default_service
