import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone 
import email.utils
from dto import ScrapedArticleDTO

class WSJScraper:
    """
    A class to scrape Wall Street Journal RSS feeds using BeautifulSoup.
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
        
        :param date_str: Date string in RFC 2822 format (e.g., "Tue, 16 Sep 2025 19:23:00 GMT").
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

    def _parse_rss_response(self, xml_content: str, num_articles: int, after_date: Optional[datetime] = None, extracted_from: str = None) -> List[ScrapedArticleDTO]:
        """
        Parse RSS XML content and extract articles from WSJ feed.
        
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

            # Extract description for additional context
            description_elem = item.find("description")
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract link
            link_elem = item.find("link")
            link = link_elem.get_text(strip=True) if link_elem else ""
            
            # For WSJ, the source is Wall Street Journal
            source = "Wall Street Journal"
            
            articles.append(ScrapedArticleDTO(
                title=title,
                source=source,
                date=article_date,
                link=link,
                short_description=description,
                extracted_from=extracted_from
            ))
        
        return articles
    
    def scrape_world_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from WSJ World News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        
        url = "https://feeds.content.dowjones.io/public/rss/RSSWorldNews"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch WSJ RSS feed: {e}")
        
        return self._parse_rss_response(response.text, num_articles, after_date, "WSJ World RSS")
