from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class BloombergScraper(BaseRSSScraper):
    """
    A class to scrape Bloomberg RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "Bloomberg"
    
    # URL patterns to exclude from scraping
    EXCLUDED_URL_PATTERNS = [
        "/news/audio/",
        "/news/videos/",
        "/news/features/"
    ]
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Filter to only include news articles (exclude audio, video, features).
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        return any(pattern in link for pattern in self.EXCLUDED_URL_PATTERNS)
    
    def scrape_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Bloomberg News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://feeds.bloomberg.com/news.rss"
        return self._scrape_feed(url, num_articles, after_date, "Bloomberg")

    def scrape_economics_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape economics news from Bloomberg News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://feeds.bloomberg.com/economics/news.rss"
        return self._scrape_feed(url, num_articles, after_date, "Bloomberg")

    def scrape_industries_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape industries news from Bloomberg News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://feeds.bloomberg.com/industries/news.rss"
        return self._scrape_feed(url, num_articles, after_date, "Bloomberg")

    def scrape_politics_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape politics news from Bloomberg News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://feeds.bloomberg.com/politics/news.rss"
        return self._scrape_feed(url, num_articles, after_date, "Bloomberg")

