from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class MarketWatchScraper(BaseRSSScraper):
    """
    A class to scrape MarketWatch RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    
    MarketWatch RSS feeds use standard RSS 2.0 format with Dublin Core (dc:creator)
    and Media RSS (media:content) extensions for author and image metadata.
    """
    
    SOURCE_NAME = "MarketWatch"
    
    def scrape_top_stories(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape top stories from MarketWatch RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.marketwatch.com/rss/topstories"
        return self._scrape_feed(url, num_articles, after_date, "MarketWatch Top Stories")