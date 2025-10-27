from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class TheGuardianScraper(BaseRSSScraper):
    """
    A class to scrape The Guardian RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "The Guardian"
    
    # URL patterns to exclude from scraping
    EXCLUDED_URL_PATTERNS = [
        "/sport/",
        "/football/",
        "/live/",
        "/gallery/",
        "/video/",
        "/crosswords/",
        "/games/",
        "/observer/",
        "/commentisfree/",
        "/ng-interactive/"
    ]
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Filter to only include news articles (exclude sport, live blogs, galleries, etc.).
        
        Guardian URLs typically have patterns like /politics/, /world/, /business/ for news,
        and /sport/, /gallery/, /video/ for non-news content.
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        return any(pattern in link for pattern in self.EXCLUDED_URL_PATTERNS)
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from RSS item element with HTML tag stripping.
        
        The Guardian descriptions contain HTML tags that need to be stripped.
        
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
        Scrape articles from The Guardian Europe RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.theguardian.com/europe/rss"
        return self._scrape_feed(url, num_articles, after_date, "The Guardian Europe RSS")
    
    def scrape_world_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from The Guardian World News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.theguardian.com/world/rss"
        return self._scrape_feed(url, num_articles, after_date, "The Guardian World RSS")