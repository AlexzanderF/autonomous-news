from typing import List, Optional
from datetime import datetime
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class YahooFinanceScraper(BaseRSSScraper):
    """
    A class to scrape Yahoo Finance RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "Yahoo Finance"
    
    def scrape_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Yahoo Finance News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://finance.yahoo.com/news/rssindex"
        return self._scrape_feed(url, num_articles, after_date, "Yahoo Finance")
