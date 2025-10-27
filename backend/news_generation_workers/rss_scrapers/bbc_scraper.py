from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO

class BBCScraper(BaseRSSScraper):
    """
    A class to scrape BBC News RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "BBC News"
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Filter to only include news articles (skip sport, sounds, etc.).
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        # BBC news articles have "/news/articles" in their URL
        return "/news/articles" not in link
    
    def scrape_international_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from BBC International News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://feeds.bbci.co.uk/news/rss.xml?edition=int"
        return self._scrape_feed(url, num_articles, after_date, "BBC International RSS")
