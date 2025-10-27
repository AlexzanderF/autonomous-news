from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class PoliticoScraper(BaseRSSScraper):
    """
    A class to scrape Politico EU RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    """
    
    SOURCE_NAME = "Politico"
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from RSS item element with HTML tag stripping.
        
        Politico descriptions contain HTML tags that need to be stripped.
        
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
        Scrape articles from Politico EU RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.politico.eu/feed/"
        return self._scrape_feed(url, num_articles, after_date, "Politico EU RSS")