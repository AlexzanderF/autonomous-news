from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO

class GoogleNewsScraper(BaseRSSScraper):
    """
    A class to scrape Google News RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    
    Note: Google News aggregates from multiple sources, so the source name
    is extracted from each item rather than using a class constant.
    """
    
    SOURCE_NAME = "Google News"  # Default fallback
    
    def _get_source_name(self, item: BeautifulSoup) -> str:
        """
        Extract the source name from the item (Google News specific).
        
        Google News RSS feeds include a <source> tag with the original publisher.
        
        :param item: BeautifulSoup item element.
        :return: Source name string.
        """
        source_elem = item.find("source")
        return source_elem.get_text(strip=True) if source_elem else self.SOURCE_NAME
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from RSS item element.
        
        Google News doesn't include descriptions, so return empty string.
        
        :param item: BeautifulSoup item element.
        :return: Empty string.
        """
        return ""
    
    def scrape_rss_by_source(self, source_domain: str, num_articles: int = 200, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from a specific news source using Google News RSS search.
        
        :param source_domain: The domain of the news source (e.g., "reuters.com", "bbc.com").
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param hl: Language code (default: "en-US").
        :param gl: Country code (default: "US").
        :param ceid: Content edition ID (default: "US:en").
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://news.google.com/rss/search"
        params = {
            "q": f"site:{source_domain}",
            "hl": hl,
            "gl": gl,
            "ceid": ceid,
        }
        return self._scrape_feed(url, num_articles, after_date, f"Google News - {source_domain}", params)
        
    def scrape_rss_by_topic(self, topic_id: str, num_articles: int = 200, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from a Google News topic RSS feed.
        
        :param topic_id: The encoded topic ID (e.g., "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB").
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param hl: Language code (default: "en-US").
        :param gl: Country code (default: "US").
        :param ceid: Content edition ID (default: "US:en").
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = f"https://news.google.com/rss/topics/{topic_id}"
        params = {
            "hl": hl,
            "gl": gl,
            "ceid": ceid,
        }
        return self._scrape_feed(url, num_articles, after_date, "Google News", params)

    def scrape_top_headlines(self, num_articles: int = 200, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape top headlines from Google News.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param hl: Language code (default: "en-US").
        :param gl: Country code (default: "US").
        :param ceid: Content edition ID (default: "US:en").
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        topic = "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB"
        return self.scrape_rss_by_topic(topic, num_articles, hl, gl, ceid, after_date)

    def scrape_top_world_headlines(self, num_articles: int = 200, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape top world headlines from Google News.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param hl: Language code (default: "en-US").
        :param gl: Country code (default: "US").
        :param ceid: Content edition ID (default: "US:en").
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        topic = "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB"
        return self.scrape_rss_by_topic(topic, num_articles, hl, gl, ceid, after_date)

    def scrape_top_business_headlines(self, num_articles: int = 200, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape top business headlines from Google News.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param hl: Language code (default: "en-US").
        :param gl: Country code (default: "US").
        :param ceid: Content edition ID (default: "US:en").
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        topic = "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB"
        return self.scrape_rss_by_topic(topic, num_articles, hl, gl, ceid, after_date)

    def scrape_top_technology_headlines(self, num_articles: int = 200, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape top technology headlines from Google News.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param hl: Language code (default: "en-US").
        :param gl: Country code (default: "US").
        :param ceid: Content edition ID (default: "US:en").
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        topic = "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB"
        return self.scrape_rss_by_topic(topic, num_articles, hl, gl, ceid, after_date)