from rss_scrapers.google_news_scraper import GoogleNewsScraper
from datetime import datetime, timedelta, timezone
import json
import os
from dto import ScrapedArticleDTO
from typing import List
from rss_scrapers.wsj_scraper import WSJScraper
from rss_scrapers.bbc_scraper import BBCScraper
from rss_scrapers.the_guardian_scraper import TheGuardianScraper
from rss_scrapers.dw_scraper import DWScraper
from rss_scrapers.euronews_scraper import EuronewsScraper
from rss_scrapers.al_jazeera_scraper import AlJazeeraScraper

def save_articles_to_json(articles: List[ScrapedArticleDTO], filename: str):
    """Save articles to JSON file with proper serialization."""
    # Convert articles to dictionaries for JSON serialization
    articles_data: List[dict] = []
    for article in articles:
        article_dict = {
            "title": article.title,
            "source": article.source,
            "date": article.date.isoformat(),  # Convert datetime to ISO string
            "link": str(article.link),  # Convert HttpUrl to string
            "short_description": article.short_description if article.short_description else "",
            "extracted_from": article.extracted_from
        }
        articles_data.append(article_dict)
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Save to JSON file
    filepath = os.path.join("output", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(articles_data)} articles to {filepath}")
    return articles_data

def main():
    after_date = datetime.now(timezone.utc) - timedelta(days=1)
    
    googleNewsScraper = GoogleNewsScraper()
    # Test 1: Scrape by topic (existing functionality)
    print("Testing topic-based scraping...")
    google_news_articles = googleNewsScraper.scrape_rss_by_topic(
        "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB", 
        after_date=after_date
    )
    save_articles_to_json(google_news_articles, "google_news_articles.json")
    
    wsj_scraper = WSJScraper()
    # Test WSJ
    wsj_articles = wsj_scraper.scrape_world_news(
        after_date=after_date
    )
    save_articles_to_json(wsj_articles, "wsj_articles.json")

    # Test BBC
    bbc_scraper = BBCScraper()
    bbc_articles = bbc_scraper.scrape_international_news(
        after_date=after_date
    )
    save_articles_to_json(bbc_articles, "bbc_articles.json")

    # Test The Guardian
    guardian_scraper = TheGuardianScraper()
    guardian_articles = guardian_scraper.scrape_world_news(
        after_date=after_date
    )
    save_articles_to_json(guardian_articles, "guardian_articles.json")
    
    # Test DW
    dw_scraper = DWScraper()
    dw_articles = dw_scraper.scrape_top_news(
        after_date=after_date
    )
    save_articles_to_json(dw_articles, "dw_articles.json")

    # Test Euronews
    euronews_scraper = EuronewsScraper()
    euronews_articles = euronews_scraper.scrape_latest_news(
        after_date=after_date
    )
    save_articles_to_json(euronews_articles, "euronews_articles.json")

    # Test Al Jazeera
    al_jazeera_scraper = AlJazeeraScraper()
    al_jazeera_articles = al_jazeera_scraper.scrape_all_news(
        after_date=after_date
    )
    save_articles_to_json(al_jazeera_articles, "al_jazeera_articles.json")

    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Google News articles: {len(google_news_articles)}")
    print(f"WSJ articles: {len(wsj_articles)}")
    print(f"BBC articles: {len(bbc_articles)}")
    print(f"Guardian articles: {len(guardian_articles)}")
    print(f"DW articles: {len(dw_articles)}")
    print(f"Euronews articles: {len(euronews_articles)}")
    print(f"Al Jazeera articles: {len(al_jazeera_articles)}")
    print(f"Total articles: {len(google_news_articles) + len(wsj_articles) + len(bbc_articles) + len(guardian_articles) + len(dw_articles) + len(euronews_articles) + len(al_jazeera_articles)}")
    
if __name__ == "__main__":
    main()