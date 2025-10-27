from typing import List, Optional
from datetime import datetime
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class WSJScraper(BaseRSSScraper):
    """
    A class to scrape Wall Street Journal RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "Wall Street Journal"
    
    def scrape_world_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from WSJ World News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://feeds.content.dowjones.io/public/rss/RSSWorldNews"
        return self._scrape_feed(url, num_articles, after_date, "WSJ World RSS")
