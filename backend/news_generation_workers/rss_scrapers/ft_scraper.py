from typing import List, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class FinancialTimesScraper(BaseRSSScraper):
    """
    A class to scrape Financial Times news sitemap using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    
    Note: FT uses Google News sitemap format instead of RSS,
    so we override the parsing methods accordingly.
    """
    
    SOURCE_NAME = "Financial Times"
    
    def _parse_iso_date(self, date_str: str) -> datetime:
        """
        Parse ISO 8601 date string to datetime object.
        
        :param date_str: Date string in ISO 8601 format (e.g., "2026-01-01T17:41:18.580Z").
        :return: Parsed datetime object, or current datetime as fallback.
        """
        if not date_str:
            return datetime.now(timezone.utc)
        
        try:
            # Handle ISO 8601 format with milliseconds
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return datetime.now(timezone.utc)
    
    def _parse_sitemap_response(
        self, 
        xml_content: str, 
        num_articles: int, 
        after_date: Optional[datetime] = None, 
        extracted_from: Optional[str] = None
    ) -> List[ScrapedArticleDTO]:
        """
        Parse Google News sitemap XML content and extract articles.
        
        :param xml_content: Raw XML content from sitemap.
        :param num_articles: Maximum number of articles to extract.
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source where the headline was extracted from.
        :return: List of ScrapedArticleDTO objects.
        """
        soup = BeautifulSoup(xml_content, "xml")
        
        # Find url elements in sitemap
        url_elements = soup.find_all("url")[:num_articles]
        
        articles = []
        for url_elem in url_elements:
            # Extract link from <loc> element
            loc_elem = url_elem.find("loc")
            link = loc_elem.get_text(strip=True) if loc_elem else ""
            
            # Extract news data from <news:news> element
            news_elem = url_elem.find("news:news")
            if not news_elem:
                continue
            
            # Extract title
            title_elem = news_elem.find("news:title")
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract publication date
            date_elem = news_elem.find("news:publication_date")
            date_str = date_elem.get_text(strip=True) if date_elem else ""
            article_date = self._parse_iso_date(date_str)
            
            # Filter by date if after_date is provided
            if after_date and article_date and article_date < after_date:
                continue
            
            # Extract keywords as description
            keywords_elem = news_elem.find("news:keywords")
            keywords = keywords_elem.get_text(strip=True) if keywords_elem else ""
            
            # Use extracted_from if provided, otherwise use source name
            extracted_from_value = extracted_from if extracted_from else self.SOURCE_NAME
            
            articles.append(ScrapedArticleDTO(
                title=title,
                source=self.SOURCE_NAME,
                date=article_date,
                link=link,
                short_description=keywords,
                extracted_from=extracted_from_value
            ))
        
        return articles
    
    def scrape_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Financial Times news sitemap.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.ft.com/sitemaps/news.xml"
        xml_content = self._fetch_rss_feed(url)
        return self._parse_sitemap_response(xml_content, num_articles, after_date, "FT News Sitemap")
