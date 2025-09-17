import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone 
import email.utils
from dto import ScrapedArticleDTO

class GoogleNewsScraper:
    """
    A class to scrape Google News RSS feeds using BeautifulSoup.
    """
    
    def __init__(self):
        """
        Initialize the scraper with a session and default headers.
        """
        self.session = requests.Session()
        default_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.session.headers.update({
            "User-Agent": default_ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
    
    def _parse_article_date(self, date_str: str) -> datetime:
        """
        Parse article date string to datetime object.
        
        :param date_str: Date string in RFC 2822 format (e.g., "Mon, 16 Sep 2024 10:30:00 GMT").
        :return: Parsed datetime object, or current datetime as fallback.
        """
        if not date_str:
            # Return timezone-aware datetime to match parsed dates
            return datetime.now(timezone.utc)
        
        try:
            # Parse RFC 2822 date format (returns timezone-aware datetime)
            return email.utils.parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            # If date parsing fails, use current datetime as fallback
            return datetime.now(timezone.utc)

    def _parse_rss_response(self, xml_content: str, num_articles: int, after_date: Optional[datetime] = None, extracted_from: str = "Google News") -> List[ScrapedArticleDTO]:
        """
        Parse RSS XML content and extract articles.
        
        :param xml_content: Raw XML content from RSS feed.
        :param num_articles: Maximum number of articles to extract.
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source where the headline was extracted from.
        :return: List of ScrapedArticleDTO objects.
        """
        soup = BeautifulSoup(xml_content, "xml")
        
        # Find item elements (story clusters)
        item_elements = soup.select("item")[:num_articles]
        
        articles = []
        for item in item_elements:
            # Extract title
            title_elem = item.find("title")
            title = title_elem.get_text(strip=True) if title_elem else ""
                        
            # Extract date/time
            pubdate_elem = item.find("pubDate")
            date_str = pubdate_elem.get_text(strip=True) if pubdate_elem else ""
            
            # Parse date to datetime object
            article_date = self._parse_article_date(date_str)
            
            # Filter by date if after_date is provided
            if after_date and article_date and article_date < after_date:
                continue  # Skip this article if it's before the cutoff date

            # Extract source (primary source)
            source_elem = item.find("source")
            source = source_elem.get_text(strip=True) if source_elem else ""
            
            # Extract link (Google News cluster link)
            link_elem = item.find("link")
            link = link_elem.get_text(strip=True) if link_elem else ""
            
            articles.append(ScrapedArticleDTO(
                title=title,
                source=source,
                date=article_date,
                link=link,
                extracted_from=extracted_from
            ))
        
        return articles
    
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
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch RSS feed for source {source_domain}: {e}")
        
        return self._parse_rss_response(response.text, num_articles, after_date, f"Google News - {source_domain}")
        
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
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch RSS feed: {e}")
        
        return self._parse_rss_response(response.text, num_articles, after_date, "Google News")