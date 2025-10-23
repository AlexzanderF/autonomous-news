import os
import json
import logging
import schedule
import time
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
import re
from pathlib import Path
from google import genai
from dotenv import load_dotenv
import redis
from dto import ScrapedArticleDTO, ProcessedHeadlineDTO

# Import existing scrapers
from rss_scrapers.google_news_scraper import GoogleNewsScraper
from rss_scrapers.wsj_scraper import WSJScraper
from rss_scrapers.bbc_scraper import BBCScraper
from rss_scrapers.the_guardian_scraper import TheGuardianScraper
from rss_scrapers.dw_scraper import DWScraper
from rss_scrapers.france24_scraper import France24Scraper
from rss_scrapers.al_jazeera_scraper import AlJazeeraScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsIngestionWorker:
    """
    A worker class that ingests news articles from RSS feeds, deduplicates
    the headlines using an LLM, and publishes the selected items to Redis.
    """
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required")

        self.genai_client = genai.Client(api_key=api_key)

        # Model configuration - can be changed via environment variables
        self.model_name = os.getenv('LLM_MODEL_NAME', 'gemini-2.5-flash')
        if not self.model_name:
            raise ValueError("LLM_MODEL_NAME environment variable is required")
        self.temperature = float(os.getenv('LLM_TEMPERATURE', 0.75))

        # Load reusable prompts from markdown files
        self.worker_dir = Path(__file__).resolve().parent
        self.pick_headlines_prompt = self._load_prompt('pick_headlines_prompt.md')

        # Redis configuration
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        redis_password = os.getenv('REDIS_PASSWORD')
        self.redis_queue_name = os.getenv('REDIS_QUEUE_NAME', 'news:headlines')
        self.redis_last_run_key = 'news:worker:last_run_timestamp'

        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password if redis_password else None,
            decode_responses=True
        )

        try:
            self.redis_client.ping()
        except redis.RedisError as exc:
            raise ConnectionError(f"Failed to connect to Redis: {exc}") from exc

        logger.info("NewsIngestionWorker initialized successfully")

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt template from a markdown file."""
        prompt_path = self.worker_dir / filename
        try:
            prompt = prompt_path.read_text(encoding='utf-8').strip()
            if not prompt:
                logger.warning(f"Prompt file {filename} is empty")
            return prompt
        except FileNotFoundError:
            logger.error(f"Prompt file {filename} not found at {prompt_path}")
            raise
        except OSError as exc:
            logger.error(f"Failed to read prompt file {filename}: {exc}")
            raise

    def get_last_run_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of the last worker run from Redis."""
        try:
            timestamp_str = self.redis_client.get(self.redis_last_run_key)
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
            return None
        except (redis.RedisError, ValueError) as exc:
            logger.warning(f"Failed to retrieve last run timestamp: {exc}")
            return None

    def set_last_run_timestamp(self, timestamp: datetime) -> bool:
        """Store the timestamp of the current worker run in Redis."""
        try:
            self.redis_client.set(self.redis_last_run_key, timestamp.isoformat())
            return True
        except redis.RedisError as exc:
            logger.error(f"Failed to store last run timestamp: {exc}")
            return False

    def fetch_all_headlines(self, after_date: datetime) -> List[ScrapedArticleDTO]:
        """
        Fetch headlines from all RSS scrapers.
        """
        logger.info(f"Fetching headlines from all sources after {after_date}")
        all_articles = []
        
        try:
            # Google News
            google_articles = GoogleNewsScraper().scrape_rss_by_topic(
                "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB",   #Headlines topic id
                after_date=after_date
            )
            all_articles.extend(google_articles)
            logger.info(f"Fetched {len(google_articles)} Google News articles")
            
            # WSJ
            wsj_articles = WSJScraper().scrape_world_news(after_date=after_date)
            all_articles.extend(wsj_articles)
            logger.info(f"Fetched {len(wsj_articles)} WSJ articles")
            
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
            
            # Al Jazeera
            al_jazeera_articles =  AlJazeeraScraper().scrape_all_news(after_date=after_date)
            all_articles.extend(al_jazeera_articles)
            logger.info(f"Fetched {len(al_jazeera_articles)} Al Jazeera articles")
            
        except Exception as e:
            logger.error(f"Error fetching headlines: {str(e)}")
            return []
        
        logger.info(f"Total headlines fetched: {len(all_articles)}")
        return all_articles
    
    def deduplicate_headlines_with_llm(self, articles: List[ScrapedArticleDTO], maxHeadlinesCount: int = 20) -> List[ProcessedHeadlineDTO]:
        """Use the selection prompt to pick top headlines for article generation."""
        if not articles:
            return []

        logger.info(f"Selecting top headlines from {len(articles)} scraped items using {self.model_name}")

        headlines_data: List[Dict[str, str]] = []
        for article in articles:
            headlines_data.append({
                'title': article.title,
                'short_description': article.short_description or "",
                'date': article.date.isoformat(),
            })

        user_message = (
            f"Current UTC time: {datetime.now(timezone.utc).isoformat()}\n"
            "Analyze the following JSON array of headlines and follow the instructions in the system prompt.\n"
            f"Return ONLY a JSON array of objects, with maximum length of {maxHeadlinesCount}.\n"
            f"Headlines JSON:\n{json.dumps(headlines_data, indent=2)}"
        )
        
        try:
            response = self.genai_client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=genai.types.GenerateContentConfig(
                    system_instruction=self.pick_headlines_prompt,
                    temperature=self.temperature,
                    response_mime_type='application/json',
                    thinking_config=genai.types.ThinkingConfig(thinking_budget=-1)
                    # response_schema=list[ProcessedHeadline]
                )
            )

            response_text = response.text.strip()
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError as exc:
                logger.error(f"Failed to parse JSON response: {exc}. Raw output: {response_text[:200]}...")
                raise

            if not isinstance(parsed_response, list):
                logger.error("LLM response did not return a JSON array")
                return []

            processed_headlines: List[ProcessedHeadlineDTO] = [ProcessedHeadlineDTO(**headline) for headline in parsed_response]

            logger.info(
                "Headline selection complete: %d stories ready for Redis publishing",
                len(processed_headlines)
            )

            return processed_headlines

        except Exception as exc:
            logger.error(f"Error selecting headlines with AI: {exc}")
            return []
    
    def push_headlines_to_queue(self, headlines: List[ProcessedHeadlineDTO]) -> int:
        """Push selected headlines onto the configured Redis queue."""
        if not headlines:
            logger.info("No headlines to publish to Redis")
            return 0

        published = 0
        for headline in headlines:
            payload = {
                'title': headline.title,
                'category': headline.category,
            }   
            try:
                self.redis_client.rpush(self.redis_queue_name, json.dumps(payload))
                published += 1
            except redis.RedisError as exc:
                logger.error(
                    "Failed to push headline '%s' to Redis queue '%s': %s",
                    headline.title,
                    self.redis_queue_name,
                    exc,
                )

        logger.info(
            "Published %d headlines to Redis queue '%s'",
            published,
            self.redis_queue_name,
        )
        return published
    
    def run_ingestion_cycle(self) -> None:
        """Fetch headlines, select the top stories, and publish them to Redis."""
        try:
            logger.info("=== Starting headline ingestion cycle ===")
            cycle_start_time = datetime.now(timezone.utc)

            # Get the last run timestamp, or fall back to 4 hours ago for first run
            last_run_timestamp = self.get_last_run_timestamp()
            if last_run_timestamp:
                after_date = last_run_timestamp
                logger.info(f"Using last run timestamp: {after_date}")
            else:
                after_date = datetime.now(timezone.utc) - timedelta(days=1)
                logger.info(f"No previous run found, using 24-hour fallback: {after_date}")
            
            all_articles = self.fetch_all_headlines(after_date)

            if not all_articles:
                logger.info("No new articles found, ending cycle")
                return

            processed_headlines = self.deduplicate_headlines_with_llm(all_articles, 20)

            if not processed_headlines:
                logger.error("No headlines processed")
                return

            self.push_headlines_to_queue(processed_headlines)

            # Store the current timestamp as the last successful run
            if self.set_last_run_timestamp(cycle_start_time):
                logger.info(f"Updated last run timestamp to: {cycle_start_time}")
            else:
                logger.warning("Failed to update last run timestamp")

            cycle_duration = datetime.now(timezone.utc) - cycle_start_time
            logger.info("=== Headline ingestion cycle completed ===")
            logger.info(
                "Duration: %s | Scraped: %d | Picked: %d",
                cycle_duration,
                len(all_articles),
                len(processed_headlines)
            )

        except Exception as exc:
            logger.error(f"Error in ingestion cycle: {exc}")
            return
    
    def start_scheduler(self) -> None:
        """
        Start the scheduled worker that runs every 4 hours.
        """
        logger.info("Starting headline ingestion worker scheduler")
        logger.info("Worker will run every 4 hours")
        
        # Schedule the job every 4 hours
        schedule.every(4).hours.do(self.run_ingestion_cycle)
        
        # Run once immediately
        self.run_ingestion_cycle()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """
    Main entry point for the worker.
    """
    try:
        worker = NewsIngestionWorker()
        logger.info("Worker initialized successfully, starting scheduler...")
        worker.start_scheduler()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main()
