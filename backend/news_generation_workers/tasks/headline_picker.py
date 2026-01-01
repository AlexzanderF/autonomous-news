import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
import redis
from google import genai
from celery import Task
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from dto import ScrapedArticleDTO, ProcessedHeadlineDTO, HeadlinePickerResponse

# Import RSS scrapers
from rss_scrapers.google_news_scraper import GoogleNewsScraper
from rss_scrapers.wsj_scraper import WSJScraper
from rss_scrapers.bbc_scraper import BBCScraper
from rss_scrapers.the_guardian_scraper import TheGuardianScraper
from rss_scrapers.dw_scraper import DWScraper
from rss_scrapers.france24_scraper import France24Scraper
from rss_scrapers.politico_scraper import PoliticoScraper
from rss_scrapers.bloomberg_scraper import BloombergScraper
from rss_scrapers.yahoo_finance_scraper import YahooFinanceScraper
from rss_scrapers.ft_scraper import FinancialTimesScraper

from celery_config import celery_app
from .shared import (
    get_redis_client,
    get_genai_client,
    load_prompt,
    logger,
    REDIS_LAST_RUN_KEY,
    HEADLINES_PICKER_MODEL_NAME,
    HEADLINES_PICKER_THINKING_BUDGET,
    HEADLINES_PICKER_THINKING_LEVEL,
    HEADLINES_PICKER_TEMPERATURE,
)

from db import Article, get_database_session

import os

# ============================================================================
# Headline Ingestion Task
# ============================================================================

@celery_app.task(bind=True, name='news_generation_workers.tasks.headline_picker.run_headline_picker_cycle')
def run_headline_picker_cycle(self: Task) -> Dict[str, Any]:
    """
    Periodic task that fetches headlines, deduplicates them using LLM,
    and queues article generation tasks.
    Runs every 4 hours via Celery Beat.
    """
    try:
        logger.info("=== Starting headline ingestion cycle ===")
        cycle_start_time = datetime.now(timezone.utc)

        redis_client = get_redis_client()

        # Get the last run timestamp, or fall back to 24 hours ago for initial run
        last_run_timestamp = get_last_run_timestamp(redis_client)
        if last_run_timestamp:
            after_date = last_run_timestamp
            logger.info(f"Using last run timestamp: {after_date}")
        else:
            after_date = datetime.now(timezone.utc) - timedelta(days=1)
            logger.info(f"No previous run found, using 24-hour fallback: {after_date}")

        # Fetch all headlines
        all_articles = fetch_all_headlines(after_date)

        if not all_articles:
            logger.info("No new articles found, ending cycle")
            return {
                'status': 'success',
                'message': 'No new articles found',
                'scraped_count': 0,
                'selected_count': 0
            }

        # Deduplicate and select top headlines using LLM
        # Calculate dynamic limit based on input count
        max_headlines = calculate_headline_limit(len(all_articles))
        processed_headlines = pick_headlines_with_llm(all_articles, max_headlines_count=max_headlines)

        if not processed_headlines:
            logger.error("No headlines processed")
            return {
                'status': 'error',
                'message': 'No headlines processed by LLM',
                'scraped_count': len(all_articles),
                'selected_count': 0
            }

        # Store the current timestamp as the last successful run
        if set_last_run_timestamp(redis_client, cycle_start_time):
            logger.info(f"Updated last run timestamp to: {cycle_start_time}")
        else:
            logger.warning("Failed to update last run timestamp")

        # Queue article generation tasks using Celery
        from .article_generation import generate_article_from_headline
        
        queued_count = 0
        for headline in processed_headlines:
            try:
                generate_article_from_headline.delay(
                    title=headline.title,
                    category=headline.category,
                    is_featured=headline.is_featured
                )
                queued_count += 1
            except Exception as exc:
                logger.error(f"Failed to queue article generation for '{headline.title}': {exc}")

        cycle_duration = datetime.now(timezone.utc) - cycle_start_time
        logger.info("=== Headline ingestion cycle completed ===")
        logger.info(
            "Duration: %s | Scraped: %d | Selected: %d | Queued: %d",
            cycle_duration,
            len(all_articles),
            len(processed_headlines),
            queued_count
        )

        return {
            'status': 'success',
            'scraped_count': len(all_articles),
            'selected_count': len(processed_headlines),
            'queued_count': queued_count,
            'duration_seconds': cycle_duration.total_seconds()
        }

    except Exception as exc:
        logger.error(f"Error in ingestion cycle: {exc}")
        return {
            'status': 'error',
            'message': str(exc)
        }


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_headline_limit(input_count: int) -> int:
    """
    Calculate the maximum number of headlines to pick based on input count.
    Progression: 0-100 → 20, 101-200 → 40, 201-300 → 60, etc.
    
    Args:
        input_count: Number of scraped headlines
        
    Returns:
        Maximum number of headlines to select (20 per 100 range, max 100)
    """
    if input_count <= 0:
        return 0
    
    # Calculate which 100-range bracket we're in (1-100 = bracket 1, 101-200 = bracket 2, etc.)
    bracket = ((input_count - 1) // 100) + 1
    
    # Each bracket gets 20 headlines
    limit = bracket * 20
    
    # Cap at 100 maximum
    return min(100, limit)


def get_last_run_timestamp(redis_client: redis.Redis) -> Optional[datetime]:
    """Get the timestamp of the last worker run from Redis."""
    try:
        timestamp_str = redis_client.get(REDIS_LAST_RUN_KEY)
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str)
        return None
    except (redis.RedisError, ValueError) as exc:
        logger.warning(f"Failed to retrieve last run timestamp: {exc}")
        return None


def set_last_run_timestamp(redis_client: redis.Redis, timestamp: datetime) -> bool:
    """Store the timestamp of the current worker run in Redis."""
    try:
        redis_client.set(REDIS_LAST_RUN_KEY, timestamp.isoformat())
        return True
    except redis.RedisError as exc:
        logger.error(f"Failed to store last run timestamp: {exc}")
        return False


def fetch_recent_article_titles(hours: int = 24) -> List[str]:
    """
    Fetch article titles from the database for deduplication.
    Returns titles from the last N hours to help LLM avoid selecting duplicate stories.
    """
    db = None
    try:
        db = get_database_session()
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_articles = db.query(Article.title).filter(
            Article.created_at >= cutoff_time
        ).all()
        
        titles = [article.title for article in recent_articles]
        logger.info(f"Fetched {len(titles)} recent article titles for deduplication")
        return titles
        
    except Exception as exc:
        logger.warning(f"Failed to fetch recent article titles: {exc}")
        return []
    finally:
        if db:
            db.close()


def fetch_all_headlines(after_date: datetime) -> List[ScrapedArticleDTO]:
    """Fetch headlines from all RSS scrapers."""
    logger.info(f"Fetching headlines from all sources after {after_date}")
    all_articles = []

    try:
        # Google News
        googleNewsScraper = GoogleNewsScraper()
        google_articles_world = googleNewsScraper.scrape_top_world_headlines(after_date=after_date)
        all_articles.extend(google_articles_world)
        logger.info(f"Fetched {len(google_articles_world)} Google News World news")

        google_articles_business = googleNewsScraper.scrape_top_business_headlines(after_date=after_date)
        all_articles.extend(google_articles_business)
        logger.info(f"Fetched {len(google_articles_business)} Google News Business Headlines")

        google_articles_technology = googleNewsScraper.scrape_top_technology_headlines(after_date=after_date)
        all_articles.extend(google_articles_technology)
        logger.info(f"Fetched {len(google_articles_technology)} Google News Technology Headlines")

        # WSJ
        wsjScraper = WSJScraper()
        wsj_articles_world = wsjScraper.scrape_world_news(after_date=after_date)
        all_articles.extend(wsj_articles_world)
        logger.info(f"Fetched {len(wsj_articles_world)} WSJ World news")

        wsj_articles_market = wsjScraper.scrape_market_news(after_date=after_date)
        all_articles.extend(wsj_articles_market)
        logger.info(f"Fetched {len(wsj_articles_market)} WSJ Market news")

        wsj_articles_economy = wsjScraper.scrape_economy_news(after_date=after_date)
        all_articles.extend(wsj_articles_economy)
        logger.info(f"Fetched {len(wsj_articles_economy)} WSJ Economy news")

        # Yahoo Finance
        yahoo_articles = YahooFinanceScraper().scrape_news(after_date=after_date)
        all_articles.extend(yahoo_articles)
        logger.info(f"Fetched {len(yahoo_articles)} Yahoo Finance news")

        # Bloomberg
        bloombergScraper = BloombergScraper()
        bloomberg_articles = bloombergScraper.scrape_news(after_date=after_date)
        all_articles.extend(bloomberg_articles)
        logger.info(f"Fetched {len(bloomberg_articles)} Bloomberg articles")

        bloomberg_articles = bloombergScraper.scrape_economics_news(after_date=after_date)
        all_articles.extend(bloomberg_articles)
        logger.info(f"Fetched {len(bloomberg_articles)} Bloomberg Economy news")

        # Financial Times
        financial_times_articles = FinancialTimesScraper().scrape_news(after_date=after_date)
        all_articles.extend(financial_times_articles)
        logger.info(f"Fetched {len(financial_times_articles)} Financial Times articles")

        # BBC
        bbc_articles = BBCScraper().scrape_international_news(after_date=after_date)
        all_articles.extend(bbc_articles)
        logger.info(f"Fetched {len(bbc_articles)} BBC articles")

        # The Guardian
        guardian_articles = TheGuardianScraper().scrape_world_news(after_date=after_date)
        all_articles.extend(guardian_articles)
        logger.info(f"Fetched {len(guardian_articles)} Guardian articles")

        # DW
        dw_articles = DWScraper().scrape_top_news(after_date=after_date)
        all_articles.extend(dw_articles)
        logger.info(f"Fetched {len(dw_articles)} DW articles")

        # France24
        france24 = France24Scraper().scrape_world_news(after_date=after_date)
        all_articles.extend(france24)
        logger.info(f"Fetched {len(france24)} France24 articles")

        # Politico
        politico_articles = PoliticoScraper().scrape_europe_news(after_date=after_date)
        all_articles.extend(politico_articles)
        logger.info(f"Fetched {len(politico_articles)} Politico articles")


    except Exception as e:
        logger.error(f"Error fetching headlines: {str(e)}")
        return []

    logger.info(f"Total headlines fetched: {len(all_articles)}")
    return all_articles


def pick_headlines_with_llm(articles: List[ScrapedArticleDTO], max_headlines_count: int = 40) -> List[ProcessedHeadlineDTO]:
    """Use the selection prompt to pick top headlines for article generation with structured output."""
    if not articles:
        return []

    logger.info(f"Selecting top headlines from {len(articles)} scraped items using {HEADLINES_PICKER_MODEL_NAME}")

    pick_headlines_prompt = load_prompt('llm_prompts/pick_headlines_prompt.md')
    genai_client = get_genai_client()

    # Fetch existing article titles for deduplication
    existing_titles = fetch_recent_article_titles(hours=12)

    headlines_data: List[Dict[str, str]] = []
    for article in articles:
        headlines_data.append({
            'title': article.title,
            'short_description': article.short_description or "",
            'date': article.date.isoformat(),
        })

    # Build user message with existing titles for deduplication
    user_message_parts = [
        "Analyze the following JSON array of headlines and follow the instructions in the system prompt.",
        f"Maximum headlines to select: {max_headlines_count}",
    ]
    
    if existing_titles:
        user_message_parts.append(
            f"\n**EXISTING ARTICLES (DO NOT SELECT DUPLICATES):**\n"
            f"The following {len(existing_titles)} articles already exist in our database. "
            f"Do NOT select any headlines that cover the same story or event as these existing articles:\n"
            f"{json.dumps(existing_titles)}"
        )
    
    user_message_parts.append(f"\nHeadlines JSON Input:\n{json.dumps(headlines_data)}")
    user_message = "\n".join(user_message_parts)

    try:
        response = genai_client.models.generate_content(
            model=HEADLINES_PICKER_MODEL_NAME,
            contents=user_message,
            config=genai.types.GenerateContentConfig(
                system_instruction=pick_headlines_prompt,
                response_mime_type='application/json',
                response_schema=HeadlinePickerResponse,
                temperature=HEADLINES_PICKER_TEMPERATURE,
                thinking_config=genai.types.ThinkingConfig(thinking_level=HEADLINES_PICKER_THINKING_LEVEL)
            )
        )

        # Parse the structured response using Pydantic
        parsed_response = HeadlinePickerResponse.model_validate_json(response.text)
        processed_headlines = parsed_response.headlines

        logger.info(
            "Headline selection complete: %d stories ready for article generation",
            len(processed_headlines)
        )

        return processed_headlines

    except Exception as exc:
        logger.error(f"Error selecting headlines with AI: {exc}")
        return []

