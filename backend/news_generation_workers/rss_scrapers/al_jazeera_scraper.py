from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class AlJazeeraScraper(BaseRSSScraper):
    """
    A class to scrape Al Jazeera RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "Al Jazeera"
    
    # URL patterns to exclude from scraping
    EXCLUDED_URL_PATTERNS = [
        "/sports/",
        "/video/",
        "/opinions/",
        "/gallery/",
        "/programmes/",
        "/shows/"
    ]
    
    # Categories to exclude
    EXCLUDED_CATEGORIES = ["sport", "tv shows", "show types"]
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Filter to focus on news articles only (exclude sports, videos, opinions, etc.).
        
        Al Jazeera URLs have patterns like:
        - /news/2025/9/16/article-title for news articles
        - /sports/ for sports content
        - /opinions/ for opinion pieces
        - /video/ for video content
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        # Skip if URL contains excluded patterns
        if any(pattern in link for pattern in self.EXCLUDED_URL_PATTERNS):
            return True
        
        # Also filter by category - Al Jazeera uses categories
        category_elem = item.find("category")
        category = category_elem.get_text(strip=True) if category_elem else ""
        
        # Skip non-news categories
        if category and category.lower() in self.EXCLUDED_CATEGORIES:
            return True
        
        return False
    
    def scrape_all_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Al Jazeera's main RSS feed (news articles only).
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        return self._scrape_feed(url, num_articles, after_date, "Al Jazeera RSS")