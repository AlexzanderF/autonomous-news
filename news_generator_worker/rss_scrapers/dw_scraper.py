import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone 
import email.utils
from dto import ScrapedArticleDTO

class DWScraper:
    """
    A class to scrape Deutsche Welle (DW) RSS feeds using BeautifulSoup.
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
        
        :param date_str: Date string in ISO format (e.g., "2025-09-16T21:42:00Z").
        :return: Parsed datetime object, or current datetime as fallback.
        """
        if not date_str:
            # Return timezone-aware datetime to match parsed dates
            return datetime.now(timezone.utc)
        
        try:
            # DW uses ISO format with Z suffix for UTC
            if date_str.endswith('Z'):
                # Remove Z and parse as UTC
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            try:
                # Fallback to RFC 2822 format parsing
                return email.utils.parsedate_to_datetime(date_str)
            except (ValueError, TypeError):
                # If all date parsing fails, use current datetime as fallback
                return datetime.now(timezone.utc)

    def _parse_rss_response(self, xml_content: str, num_articles: int, after_date: Optional[datetime] = None, extracted_from: str = None) -> List[ScrapedArticleDTO]:
        """
        Parse RSS XML content and extract articles from DW feed.
        
        :param xml_content: Raw XML content from RSS feed.
        :param num_articles: Maximum number of articles to extract.
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source where the headline was extracted from.
        :return: List of ScrapedArticleDTO objects.
        """
        soup = BeautifulSoup(xml_content, "xml")
        
        # DW uses Atom format, so look for entry elements instead of item
        entry_elements = soup.select("entry")[:num_articles]
        
        articles = []
        for entry in entry_elements:
            # Extract link - DW uses <link href="..."/> format in Atom
            link_elem = entry.find("link")
            link = ""
            if link_elem:
                # Atom format uses href attribute
                link = link_elem.get("href", "") if link_elem.get("href") else link_elem.get_text(strip=True)
            
            # Extract title - DW uses CDATA sections
            title_elem = entry.find("title")
            title = title_elem.get_text(strip=True) if title_elem else ""
                        
            # Extract date/time - DW uses <updated> or <published> in Atom format
            date_elem = entry.find("updated") or entry.find("published")
            date_str = date_elem.get_text(strip=True) if date_elem else ""
            
            # Parse date to datetime object
            article_date = self._parse_article_date(date_str)
            
            # Filter by date if after_date is provided
            if after_date and article_date and article_date < after_date:
                continue  # Skip this article if it's before the cutoff date

            # Extract summary/content for additional context
            summary_elem = entry.find("summary") or entry.find("content")
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # For DW, the source is Deutsche Welle
            source = "Deutsche Welle"
            
            articles.append(ScrapedArticleDTO(
                title=title,
                source=source,
                date=article_date,
                link=link,
                short_description=summary,
                extracted_from=extracted_from
            ))
        
        return articles
    
    def scrape_top_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from DW Top News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        
        url = "https://rss.dw.com/atom/rss-en-top"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch DW RSS feed: {e}")
        
        return self._parse_rss_response(response.text, num_articles, after_date, "DW Top News RSS")