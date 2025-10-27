from typing import List, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import email.utils
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO

class DWScraper(BaseRSSScraper):
    """
    A class to scrape Deutsche Welle (DW) RSS feeds using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    
    Note: DW uses Atom format instead of standard RSS, so this scraper
    overrides several methods to handle the different XML structure.
    """
    
    SOURCE_NAME = "Deutsche Welle"
    
    def _parse_article_date(self, date_str: str) -> datetime:
        """
        Parse article date string to datetime object.
        
        DW uses ISO format (e.g., "2025-09-16T21:42:00Z") instead of RFC 2822.
        
        :param date_str: Date string in ISO format.
        :return: Parsed datetime object, or current datetime as fallback.
        """
        if not date_str:
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
    
    def _extract_link(self, item: BeautifulSoup) -> str:
        """
        Extract link from Atom entry element.
        
        DW uses Atom format with <link href="..."/> instead of <link>text</link>.
        
        :param item: BeautifulSoup entry element.
        :return: Article URL string.
        """
        link_elem = item.find("link")
        if link_elem:
            # Atom format uses href attribute
            return link_elem.get("href", "") if link_elem.get("href") else link_elem.get_text(strip=True)
        return ""
    
    def _extract_date(self, item: BeautifulSoup) -> datetime:
        """
        Extract and parse publication date from Atom entry element.
        
        DW uses <updated> or <published> tags instead of <pubDate>.
        
        :param item: BeautifulSoup entry element.
        :return: Parsed datetime object.
        """
        date_elem = item.find("updated") or item.find("published")
        date_str = date_elem.get_text(strip=True) if date_elem else ""
        return self._parse_article_date(date_str)
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from Atom entry element.
        
        DW uses <summary> or <content> tags instead of <description>.
        
        :param item: BeautifulSoup entry element.
        :return: Article summary/content string.
        """
        summary_elem = item.find("summary") or item.find("content")
        return summary_elem.get_text(strip=True) if summary_elem else ""
    
    def _parse_rss_response(
        self, 
        xml_content: str, 
        num_articles: int, 
        after_date: Optional[datetime] = None, 
        extracted_from: Optional[str] = None
    ) -> List[ScrapedArticleDTO]:
        """
        Parse Atom XML content and extract articles (overridden for Atom format).
        
        DW uses Atom format with <entry> elements instead of <item> elements.
        
        :param xml_content: Raw XML content from feed.
        :param num_articles: Maximum number of articles to extract.
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source where the headline was extracted from.
        :return: List of ScrapedArticleDTO objects.
        """
        soup = BeautifulSoup(xml_content, "xml")
        
        # DW uses Atom format - look for entry elements instead of item
        item_elements = soup.select("entry")[:num_articles]
        
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
    
    def scrape_top_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from DW Top News RSS feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://rss.dw.com/atom/rss-en-top"
        return self._scrape_feed(url, num_articles, after_date, "DW Top News RSS")