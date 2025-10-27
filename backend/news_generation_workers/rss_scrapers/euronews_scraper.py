from typing import List, Optional
from datetime import datetime
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class EuronewsScraper(BaseRSSScraper):
    """
    A class to scrape Euronews RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "Euronews"
    
    def _fetch_rss_feed(self, url: str, params: Optional[dict] = None) -> str:
        """
        Fetch RSS feed content from the given URL with custom encoding handling.
        
        Euronews requires UTF-8 encoding handling.
        
        :param url: RSS feed URL.
        :param params: Optional query parameters.
        :return: Raw XML content as string.
        :raises ValueError: If the request fails.
        """
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Ensure proper encoding handling - Euronews returns UTF-8
            if response.encoding != 'utf-8':
                response.encoding = 'utf-8'
            
            return response.text
        except Exception as e:
            raise ValueError(f"Failed to fetch RSS feed from {url}: {e}")
    
    def scrape_latest_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Euronews latest news RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.euronews.com/rss"
        return self._scrape_feed(url, num_articles, after_date, "Euronews RSS")