from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class France24Scraper(BaseRSSScraper):
    """
    A class to scrape France 24 RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "France 24"
    
    # URL patterns to exclude from scraping
    EXCLUDED_URL_PATTERNS = ["/tv-shows/"]
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Filter out TV shows but keep video content as it often contains substantial news.
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        return any(pattern in link for pattern in self.EXCLUDED_URL_PATTERNS)
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from RSS item element with HTML tag stripping.
        
        France 24 descriptions contain HTML tags that need to be stripped.
        
        :param item: BeautifulSoup item element.
        :return: Article description string with HTML tags removed.
        """
        description_elem = item.find("description")
        if description_elem:
            # Parse the description content as HTML to strip tags
            description_soup = BeautifulSoup(description_elem.get_text(), "html.parser")
            return description_soup.get_text(strip=True)
        return ""
    
    def scrape_europe_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from France 24 Europe RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.france24.com/en/europe/rss"
        return self._scrape_feed(url, num_articles, after_date, "France 24 Europe RSS")
    
    def scrape_world_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from France 24 World News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.france24.com/en/rss"
        return self._scrape_feed(url, num_articles, after_date, "France 24 World RSS")