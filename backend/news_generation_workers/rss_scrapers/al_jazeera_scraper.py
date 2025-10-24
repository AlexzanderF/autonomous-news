import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone 
import email.utils
import html
from dto import ScrapedArticleDTO

class AlJazeeraScraper:
    """
    A class to scrape Al Jazeera RSS feeds using BeautifulSoup.
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
        
        :param date_str: Date string in RFC 2822 format (e.g., "Tue, 16 Sep 2025 23:52:43 +0000").
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
        Parse RSS XML content and extract articles from Al Jazeera feed.
        
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
            # Extract link first to filter out non-news content
            link_elem = item.find("link")
            link = link_elem.get_text(strip=True) if link_elem else ""
            
            # Filter to focus on news articles - Al Jazeera URLs have patterns like:
            # /news/2025/9/16/article-title for news articles
            # /sports/ for sports content
            # /opinions/ for opinion pieces
            # /video/ for video content
            excluded_patterns = [
                "/sports/",
                "/video/",
                "/opinions/",  # Remove if you want opinion pieces
                "/gallery/",
                "/programmes/",
                "/shows/"
            ]
            
            # Skip if URL contains excluded patterns (focus on news only)
            if any(pattern in link for pattern in excluded_patterns):
                continue
            
            # Also filter by category - Al Jazeera uses categories
            category_elem = item.find("category")
            category = category_elem.get_text(strip=True) if category_elem else ""
            
            # Skip non-news categories
            if category and category.lower() in ["sport", "tv shows", "show types"]:
                continue
            
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

            # Extract description for additional context and decode HTML entities
            description_elem = item.find("description")
            if description_elem:
                raw_description = description_elem.get_text(strip=True)
                # Decode HTML entities like &#039; to their actual characters
                description = html.unescape(raw_description)
            else:
                description = ""
            
            # For Al Jazeera, the source is Al Jazeera
            source = "Al Jazeera"
            
            articles.append(ScrapedArticleDTO(
                title=title,
                source=source,
                date=article_date,
                link=link,
                short_description=description,
                extracted_from=extracted_from
            ))
        
        return articles
    
    def scrape_all_news(self, num_articles: int = 200, after_date: Optional[datetime] = None) -> List[ScrapedArticleDTO]:
        """
        Scrape articles from Al Jazeera's main RSS feed (news articles only).
        
        :param num_articles: Maximum number of articles to scrape (default: 200).
        :param after_date: Optional datetime to filter articles published after this date.
        :return: List of ScrapedArticleDTO objects with article data.
        """
        
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch Al Jazeera RSS feed: {e}")
        
        return self._parse_rss_response(response.text, num_articles, after_date, "Al Jazeera RSS")