from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseRSSScraper
from dto import ScrapedArticleDTO


class ReutersScraper(BaseRSSScraper):
    """
    A class to scrape Reuters news sitemap XML feed using BeautifulSoup.
    Inherits common functionality from BaseRSSScraper.
    
    Note: Reuters uses a sitemap-news format instead of standard RSS,
    so we override the parsing methods to handle the different XML structure.
    """
    
    SOURCE_NAME = "Reuters"
    
    def _extract_link(self, item: BeautifulSoup) -> str:
        """
        Extract link from sitemap url element.
        In sitemap format, the link is in <loc> tag.
        
        :param item: BeautifulSoup url element.
        :return: Article URL string.
        """
        loc_elem = item.find("loc")
        return loc_elem.get_text(strip=True) if loc_elem else ""
    
    def _extract_title(self, item: BeautifulSoup) -> str:
        """
        Extract title from sitemap url element.
        In sitemap-news format, the title is in <news:title> tag.
        
        :param item: BeautifulSoup url element.
        :return: Article title string.
        """
        # Try news:title first
        title_elem = item.find("news:title")
        if title_elem:
            return title_elem.get_text(strip=True)
        
        # Fallback to regular title
        title_elem = item.find("title")
        return title_elem.get_text(strip=True) if title_elem else ""
    
    def _extract_date(self, item: BeautifulSoup) -> datetime:
        """
        Extract and parse publication date from sitemap url element.
        In sitemap-news format, the date is in <news:publication_date> tag.
        
        :param item: BeautifulSoup url element.
        :return: Parsed datetime object.
        """
        # Try news:publication_date first
        date_elem = item.find("news:publication_date")
        if date_elem:
            date_str = date_elem.get_text(strip=True)
            return self._parse_article_date(date_str)
        
        # Fallback to lastmod
        lastmod_elem = item.find("lastmod")
        if lastmod_elem:
            date_str = lastmod_elem.get_text(strip=True)
            return self._parse_article_date(date_str)
        
        return self._parse_article_date("")
    
    def _extract_description(self, item: BeautifulSoup) -> str:
        """
        Extract description from sitemap url element.
        Reuters sitemap doesn't include descriptions, so we use
        image caption as a fallback if available.
        
        :param item: BeautifulSoup url element.
        :return: Description string (may be empty).
        """
        # Try image caption as a fallback description
        caption_elem = item.find("image:caption")
        if caption_elem:
            return caption_elem.get_text(strip=True)
        return ""
    
    def _parse_sitemap_response(
        self,
        xml_content: str,
        num_articles: int,
        after_date: Optional[datetime] = None,
        extracted_from: Optional[str] = None
    ) -> List[ScrapedArticleDTO]:
        """
        Parse Reuters sitemap XML content and extract articles.
        
        This method handles the sitemap format which uses <url> elements
        instead of RSS <item> elements.
        
        :param xml_content: Raw XML content from sitemap feed.
        :param num_articles: Maximum number of articles to extract.
        :param after_date: Optional datetime to filter articles published after this date.
        :param extracted_from: Source where the headline was extracted from.
        :return: List of ScrapedArticleDTO objects.
        """
        soup = BeautifulSoup(xml_content, "xml")
        
        # Find url elements (sitemap format uses <url> instead of <item>)
        url_elements = soup.find_all("url")[:num_articles]
        
        articles = []
        for item in url_elements:
            # Extract link first for filtering
            link = self._extract_link(item)
            
            # Hook method: Allow subclasses to skip articles based on custom criteria
            if self._should_skip_article(item, link):
                continue
            
            # Extract article data
            title = self._extract_title(item)
            
            # Skip if no title found
            if not title:
                continue
            
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
    
    def scrape_news(
        self,
        num_articles: int = 200,
        after_date: Optional[datetime] = None
    ) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Reuters news sitemap feed.
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        url = "https://www.reuters.com/arc/outboundfeeds/news-sitemap/?outputType=xml"
        xml_content = self._fetch_rss_feed(url)
        return self._parse_sitemap_response(
            xml_content,
            num_articles,
            after_date,
            "Reuters Sitemap"
        )
