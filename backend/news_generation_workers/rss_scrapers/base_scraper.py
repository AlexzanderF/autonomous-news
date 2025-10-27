from abc import ABC, abstractmethod
import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import email.utils
import html
from dto import ScrapedArticleDTO

class BaseRSSScraper(ABC):
    """
    Abstract base class for RSS feed scrapers.
    
    This class implements the Template Method pattern, providing common functionality
    for all RSS scrapers while allowing subclasses to customize specific behaviors.
    
    Design Principles Applied:
    - DRY (Don't Repeat Yourself): Common code is centralized
    - Open/Closed Principle: Open for extension, closed for modification
    - Template Method Pattern: Defines the skeleton of scraping algorithm
    - Single Responsibility: Each method has one clear purpose
    """
    
    # Default source name (can be overridden by subclasses)
    SOURCE_NAME = "Unknown Source"
    
    # Default user agent (can be overridden by subclasses if needed)
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    def __init__(self):
        """
        Initialize the scraper with a session and default headers.
        Subclasses can override this to add custom initialization logic.
        """
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create and configure a requests session with appropriate headers.
        
        :return: Configured requests.Session object.
        """
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        return session
    
    def _parse_article_date(self, date_str: str) -> datetime:
        """
        Parse article date string to datetime object.
        
        :param date_str: Date string in RFC 2822 format (e.g., "Tue, 16 Sep 2025 23:52:43 +0000").
        :return: Parsed datetime object, or current datetime as fallback.
        """
        if not date_str:
            return datetime.now(timezone.utc)
        
        try:
            # Parse RFC 2822 date format (returns timezone-aware datetime)
            return email.utils.parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            # If date parsing fails, use current datetime as fallback
            return datetime.now(timezone.utc)
    
    def _fetch_rss_feed(self, url: str, params: Optional[dict] = None) -> str:
        """
        Fetch RSS feed content from the given URL.
        
        :param url: RSS feed URL.
        :param params: Optional query parameters.
        :return: Raw XML content as string.
        :raises ValueError: If the request fails.
        """
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch RSS feed from {url}: {e}")
    
    def _should_skip_article(self, item: BeautifulSoup, link: str) -> bool:
        """
        Determine if an article should be skipped based on source-specific criteria.
        
        This is a hook method that subclasses can override to implement custom
        filtering logic (e.g., exclude sports, videos, opinion pieces).
        
        :param item: BeautifulSoup item element from RSS feed.
        :param link: Article URL.
        :return: True if article should be skipped, False otherwise.
        """
        return False
    
    def _extract_title(self, item: BeautifulSoup) -> str:
        """
        Extract title from RSS item element.
        
        :param item: BeautifulSoup item element.
        :return: Article title string.
        """
        title_elem = item.find("title")
        return title_elem.get_text(strip=True) if title_elem else ""
    
    def _extract_link(self, item: BeautifulSoup) -> str:
        """
        Extract link from RSS item element.
        
        :param item: BeautifulSoup item element.
        :return: Article URL string.
        """
        link_elem = item.find("link")
        return link_elem.get_text(strip=True) if link_elem else ""
    
    def _extract_date(self, item: BeautifulSoup) -> datetime:
        """
        Extract and parse publication date from RSS item element.
        
        :param item: BeautifulSoup item element.
        :return: Parsed datetime object.
        """
        pubdate_elem = item.find("pubDate")
        date_str = pubdate_elem.get_text(strip=True) if pubdate_elem else ""
        return self._parse_article_date(date_str)
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from RSS item element.
        
        This method can be overridden by subclasses to handle source-specific
        description formats (e.g., HTML stripping, entity decoding).
        
        :param item: BeautifulSoup item element.
        :return: Article description string.
        """
        description_elem = item.find("description")
        if description_elem:
            raw_description = description_elem.get_text(strip=True)
            # Decode HTML entities like &#039; to their actual characters
            return html.unescape(raw_description)
        return ""
    
    def _get_source_name(self, item: BeautifulSoup) -> str:
        """
        Get the source name for an article.
        
        By default, returns the class-level SOURCE_NAME constant.
        Subclasses can override this to extract source from the item itself
        (e.g., for Google News which aggregates multiple sources).
        
        :param item: BeautifulSoup item element.
        :return: Source name string.
        """
        return self.SOURCE_NAME
    
    def _parse_rss_response(
        self, 
        xml_content: str, 
        num_articles: int, 
        after_date: Optional[datetime] = None, 
        extracted_from: Optional[str] = None
    ) -> List[ScrapedArticleDTO]:
        """
        Parse RSS XML content and extract articles (Template Method).
        
        This method defines the skeleton of the parsing algorithm.
        Subclasses can customize behavior by overriding hook methods.
        
        :param xml_content: Raw XML content from RSS feed.
        :param num_articles: Maximum number of articles to extract.
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source where the headline was extracted from.
        :return: List of ScrapedArticleDTO objects.
        """
        soup = BeautifulSoup(xml_content, "xml")
        
        # Find item elements
        item_elements = soup.select("item")[:num_articles]
        
        articles = []
        for item in item_elements:
            # Extract link first for filtering
            link = self._extract_link(item)
            
            # Hook method: Allow subclasses to skip articles based on custom criteria
            if self._should_skip_article(item, link):
                continue
            
            # Extract article data
            title = self._extract_title(item)
            article_date = self._extract_date(item)
            
            # Filter by date if after_date is provided
            if after_date and article_date and article_date < after_date:
                continue
            
            description = self._extract_description(item)
            source = self._get_source_name(item)
            
            # Use extracted_from if provided, otherwise use source name
            extracted_from_value = extracted_from if extracted_from else source
            
            articles.append(ScrapedArticleDTO(
                title=title,
                source=source,
                date=article_date,
                link=link,
                short_description=description,
                extracted_from=extracted_from_value
            ))
        
        return articles
    
    def _scrape_feed(
        self, 
        url: str, 
        num_articles: int = 200, 
        after_date: Optional[datetime] = None,
        extracted_from: Optional[str] = None,
        params: Optional[dict] = None
    ) -> List[ScrapedArticleDTO]:
        """
        Generic method to scrape an RSS feed.
        
        This is a convenience method that combines fetching and parsing.
        Most scraper methods can use this instead of duplicating code.
        
        :param url: RSS feed URL.
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source description (e.g., "BBC International RSS").
        :param params: Optional query parameters for the request.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        xml_content = self._fetch_rss_feed(url, params)
        return self._parse_rss_response(xml_content, num_articles, after_date, extracted_from)

