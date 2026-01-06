from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class CNBCScraper(BaseRSSScraper):
    """
    A class to scrape CNBC RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    
    CNBC RSS feeds use standard RSS 2.0 format with additional metadata
    namespaces for content type and sponsorship information.
    """
    
    SOURCE_NAME = "CNBC"
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Filter to exclude sponsored content.
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        # Check for sponsored content using metadata:sponsored element
        sponsored_elem = item.find("metadata:sponsored")
        if sponsored_elem and sponsored_elem.get_text(strip=True).lower() == "true":
            return True
        return False
    
    def scrape_world_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape international/world news from CNBC RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.cnbc.com/id/100727362/device/rss/rss.html"
        return self._scrape_feed(url, num_articles, after_date, "CNBC World")
    
    def scrape_top_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape top news from CNBC RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
        return self._scrape_feed(url, num_articles, after_date, "CNBC Top News")
    
    def scrape_economy_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape economy news from CNBC RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.cnbc.com/id/20910258/device/rss/rss.html"
        return self._scrape_feed(url, num_articles, after_date, "CNBC Economy")
    
    def scrape_finance_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape finance news from CNBC RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.cnbc.com/id/10000664/device/rss/rss.html"
        return self._scrape_feed(url, num_articles, after_date, "CNBC Finance")
    
    def scrape_politics_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape politics news from CNBC RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.cnbc.com/id/10000113/device/rss/rss.html"
        return self._scrape_feed(url, num_articles, after_date, "CNBC Politics")
