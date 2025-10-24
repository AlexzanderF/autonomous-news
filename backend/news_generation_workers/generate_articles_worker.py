import os
import json
import logging
import schedule
import time
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
import re
from pathlib import Path
from google import genai
from dotenv import load_dotenv
import redis
from slugify import slugify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dto import ProcessedHeadlineDTO, GeneratedArticleDTO
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from db.models import Article, Source, Category, Base
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('article_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsArticleGenerationWorker:
    """
    A worker class that consumes headlines from Redis queue and generates
    full news articles using Gemini AI with search/grounding capabilities.
    """
    
    def __init__(self):
        # Initialize Google GenAI client
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required")

        self.genai_client = genai.Client(api_key=api_key)

        # Model configuration - can be changed via environment variables
        self.model_name = os.getenv('LLM_MODEL_NAME', 'gemini-2.5-flash')
        if not self.model_name:
            raise ValueError("LLM_MODEL_NAME environment variable is required")
        self.temperature = float(os.getenv('LLM_TEMPERATURE', 0.5))  # Lower temp for factual articles

        # Load reusable prompts from markdown files
        self.worker_dir = Path(__file__).resolve().parent
        self.article_prompt = self._load_prompt('llm_prompts/generate_news_article_prompt.md')

        # Redis configuration
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        redis_password = os.getenv('REDIS_PASSWORD')
        
        # Queue names
        self.redis_headlines_queue = os.getenv('REDIS_QUEUE_NAME', 'news:headlines')
        
        # Processing tracking
        self.max_concurrent_processing = int(os.getenv('MAX_CONCURRENT_ARTICLES', '1'))
        self.check_interval_minutes = int(os.getenv('CHECK_INTERVAL_MINUTES', '1'))

        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password if redis_password else None,
            decode_responses=True,
        )

        try:
            self.redis_client.ping()
        except redis.RedisError as exc:
            raise ConnectionError(f"Failed to connect to Redis: {exc}") from exc

        # Database configuration
        db_url = os.getenv('DB_URL')
        if not db_url:
            raise ValueError("DB_URL environment variable is required")

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info("NewsArticleGenerationWorker initialized successfully")

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

    def get_database_session(self) -> Session:
        """Create and return a new database session."""
        return self.SessionLocal()

    def get_or_create_source(self, db: Session, source_url: str) -> Source:
        """Get or create a source based on URL from Gemini search results."""
        # Check if source already exists by URL
        existing_source = db.query(Source).filter(Source.url == source_url).first()
        if existing_source:
            return existing_source
        
        # Parse URL to extract domain
        parsed_url = urlparse(source_url)
        domain = parsed_url.netloc.lower()
        
        # Clean up common prefixes from domain
        domain = domain.replace('www.', '')
            
        # Create new source
        source = Source(
            url=source_url,
            domain=domain
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

    def get_or_create_category(self, db: Session, category_name: str) -> Category:
        """Get or create a category by name."""
        category = db.query(Category).filter(Category.name == category_name).first()
        if not category:
            category = Category(
                name=category_name,
            )
            db.add(category)
            db.commit()
            db.refresh(category)
        return category

    def generate_unique_slug(self, db: Session, title: str) -> str:
        """Generate a unique slug for the article."""
        base_slug = slugify(title)
        if len(base_slug) > 450:  # Leave room for suffix
            base_slug = base_slug[:450]
        
        # Check if slug exists
        existing = db.query(Article).filter(Article.slug == base_slug).first()
        if not existing:
            return base_slug
        
        # If exists, add a number suffix
        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            existing = db.query(Article).filter(Article.slug == new_slug).first()
            if not existing:
                return new_slug
            counter += 1

    def extract_sources_from_gemini_response(self, response) -> List[str]:
        """Extract source URLs from Gemini's search/grounding response."""
        sources = []
        
        try:
            # Check if response has grounding metadata with sources
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Look for grounding metadata
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_metadata = candidate.grounding_metadata
                    
                    # Extract URLs from grounding_chunks (the actual web sources)
                    # According to API docs: groundingChunks contains objects with web.uri and web.title
                    if hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks:
                        logger.info(f"Found {len(grounding_metadata.grounding_chunks)} grounding chunks")
                        
                        for idx, chunk in enumerate(grounding_metadata.grounding_chunks):
                            # Each chunk has a 'web' attribute with 'uri' and 'title'
                            if hasattr(chunk, 'web') and chunk.web:
                                # The title field contains the domain name (e.g., "aljazeera.com", "bbc.com")
                                # The uri field contains a redirect URL through vertexaisearch.cloud.google.com
                                
                                if hasattr(chunk.web, 'title') and chunk.web.title:
                                    title = chunk.web.title.strip()
                                    
                                    # If title is already a full URL, use it directly
                                    if title.startswith(('http://', 'https://')):
                                        sources.append(title)
                                        logger.debug(f"Chunk {idx}: Found full URL in title: {title}")
                                    else:
                                        # Title contains domain name, construct HTTPS URL
                                        # Clean up the domain (remove any paths or extra characters)
                                        domain = title.split('/')[0].strip()
                                        if domain and '.' in domain:  # Basic domain validation
                                            constructed_url = f"https://{domain}"
                                            sources.append(constructed_url)
                                            logger.debug(f"Chunk {idx}: Constructed URL from domain '{domain}': {constructed_url}")
                                
                                # Log the redirect URL for debugging purposes
                                if hasattr(chunk.web, 'uri') and chunk.web.uri:
                                    logger.debug(f"Chunk {idx}: Redirect URL: {chunk.web.uri}")
                    
                    # Log web search queries used (for debugging)
                    if hasattr(grounding_metadata, 'web_search_queries') and grounding_metadata.web_search_queries:
                        logger.info(f"Web search queries used: {grounding_metadata.web_search_queries}")
                
                # Also check citation metadata if available (fallback)
                if hasattr(candidate, 'citation_metadata') and candidate.citation_metadata:
                    citations = getattr(candidate.citation_metadata, 'citation_sources', [])
                    for citation in citations:
                        if hasattr(citation, 'uri') and citation.uri:
                            # Only use non-redirect URLs from citations
                            if 'vertexaisearch.cloud.google.com' not in citation.uri:
                                sources.append(citation.uri)
                                logger.debug(f"Found citation source: {citation.uri}")
                            
        except Exception as exc:
            logger.warning(f"Could not extract sources from Gemini response: {exc}", exc_info=True)
            
        # Use Set to efficiently remove duplicates and filter valid URLs
        unique_sources = {
            source for source in sources 
            if source.startswith(('http://', 'https://')) and len(source.strip()) > 8
        }
                
        logger.info(f"Extracted {len(unique_sources)} unique sources from Gemini response")
        if unique_sources:
            logger.info(f"Sources: {list(unique_sources)}")
        else:
            logger.warning("No sources extracted - this may indicate the response structure has changed")
        
        return list(unique_sources)  # Return all unique sources, no limit

    def get_headlines_from_queue(self, batch_size: int = 5) -> List[Dict[str, Any]]:
        """Get headlines from Redis queue."""
        headlines = []
        try:
            for _ in range(batch_size):
                headline_data = self.redis_client.lpop(self.redis_headlines_queue)
                if not headline_data:
                    break
                
                try:
                    headline = json.loads(headline_data)
                    headlines.append(headline)
                except json.JSONDecodeError as exc:
                    logger.error(f"Failed to parse headline data: {exc}. Raw data: {headline_data}")
                    continue
                    
        except redis.RedisError as exc:
            logger.error(f"Failed to fetch headlines from Redis queue: {exc}")
            
        logger.info(f"Retrieved {len(headlines)} headlines from queue")
        return headlines

    def generate_article_with_search(self, headline: Dict[str, Any]) -> Optional[GeneratedArticleDTO]:
        """Generate a full news article using Gemini with search/grounding."""
        try:
            title = headline.get('title', '')
            category = headline.get('category', 'General')
            
            if not title:
                logger.warning("Empty title received, skipping article generation")
                return None

            logger.info(f"Generating article for headline: {title[:50]}...")

            # Replace placeholder in the prompt template
            article_prompt = self.article_prompt.replace('{Topic Placeholder}', title)
            
            # Enable search grounding and thinking for real-time information and better reasoning
            response = self.genai_client.models.generate_content(
                contents=article_prompt,
                model=self.model_name,
                config=genai.types.GenerateContentConfig(
                    temperature=self.temperature,
                    tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())],
                    thinking_config=genai.types.ThinkingConfig(
                        thinking_budget=-1  # Unlimited thinking budget for best quality
                    )
                )
            )

            if not response or not response.text:
                logger.error(f"Empty response from Gemini for headline: {title}")
                return None

            article_content = response.text.strip()
            
            # Extract sources from Gemini's search/grounding response
            source_urls = self.extract_sources_from_gemini_response(response)
            
            # Create GeneratedArticle object with source URLs
            generated_article = GeneratedArticleDTO(
                title=title,
                category=category,
                content=article_content,
                generated_at=datetime.now(timezone.utc),
                status="draft"
            )
            
            # Add source URLs to the DTO for processing in store method
            generated_article.source_urls = source_urls

            logger.info(f"Successfully generated article for: {title[:50]}... (Length: {len(article_content)} chars)")
            return generated_article

        except Exception as exc:
            logger.error(f"Error generating article for headline '{headline.get('title', 'unknown')}': {exc}")
            return None

    def store_generated_article(self, article: GeneratedArticleDTO) -> bool:
        """Store the generated article in PostgreSQL database with multiple sources."""
        db = None
        try:
            db = self.get_database_session()
            
            # Get or create category
            category = self.get_or_create_category(db, article.category)
            
            # Generate unique slug
            slug = self.generate_unique_slug(db, article.title)
            
            # Create the Article record
            db_article = Article(
                title=article.title,
                slug=slug,
                content=article.content,
                status='published',
                ai_model_used=self.model_name,
                published_at=article.generated_at,
                created_at=article.generated_at,
                updated_at=article.generated_at
            )
            
            # Add the article to the session
            db.add(db_article)
            db.commit()
            db.refresh(db_article)
            
            # Associate with category
            db_article.categories.append(category)
            
            # Associate with sources from Gemini search/grounding
            source_count = 0
            if hasattr(article, 'source_urls') and article.source_urls:
                for source_url in article.source_urls:
                    try:
                        source = self.get_or_create_source(db, source_url)
                        db_article.sources.append(source)
                        source_count += 1
                    except Exception as exc:
                        logger.warning(f"Failed to create source for URL '{source_url}': {exc}")
                        continue
            
            db.commit()
            
            logger.info(f"Stored article in database: {article.title[:50]}... (ID: {db_article.id}, Sources: {source_count})")
            return True
            
        except Exception as exc:
            if db:
                db.rollback()
            logger.error(f"Failed to store article '{article.title}' in database: {exc}")
            return False
            
        finally:
            if db:
                db.close()

    def process_articles_batch(self) -> None:
        """Process a batch of headlines and generate articles."""
        try:
            logger.info("=== Starting article generation batch ===")
            batch_start_time = datetime.now(timezone.utc)

            # Get headlines from queue
            headlines = self.get_headlines_from_queue(batch_size=self.max_concurrent_processing)
            
            if not headlines:
                logger.info("No headlines available for processing")
                return

            generated_count = 0
            failed_count = 0

            for headline in headlines:
                try:
                    article = self.generate_article_with_search(headline)
                    if article:
                        if self.store_generated_article(article):
                            generated_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as exc:
                    logger.error(f"Unexpected error processing headline: {exc}")
                    failed_count += 1

            batch_duration = datetime.now(timezone.utc) - batch_start_time
            logger.info("=== Article generation batch completed ===")
            logger.info(
                "Duration: %s | Processed: %d | Generated: %d | Failed: %d",
                batch_duration,
                len(headlines),
                generated_count,
                failed_count
            )

        except Exception as exc:
            logger.error(f"Error in article generation batch: {exc}")

    def process_headlines_job(self) -> None:
        """
        Job function that processes available headlines.
        """
        try:
            headlines = self.get_headlines_from_queue(batch_size=self.max_concurrent_processing)
            
            if headlines:
                logger.info(f"📰 Found {len(headlines)} headlines to process")
                
                for headline in headlines:
                    try:
                        logger.info(f"🔄 Processing: {headline.get('title', 'Unknown')[:50]}...")
                        
                        article = self.generate_article_with_search(headline)
                        if article:
                            if self.store_generated_article(article):
                                logger.info(f"✅ Successfully processed: {headline.get('title', 'Unknown')[:50]}...")
                            else:
                                logger.error(f"❌ Failed to store: {headline.get('title', 'Unknown')[:50]}...")
                        else:
                            logger.error(f"❌ Failed to generate: {headline.get('title', 'Unknown')[:50]}...")
                            
                    except Exception as exc:
                        logger.error(f"❌ Error processing headline: {exc}")
                        continue
            else:
                logger.debug("💤 No headlines found")
                
        except Exception as exc:
            logger.error(f"❌ Unexpected error in job: {exc}")

    def start_simple_worker(self) -> None:
        """
        Simple worker using schedule library to check for headlines every minute.
        """
        logger.info("🚀 Starting simple article generation worker")
        logger.info(f"⏰ Using schedule library to check every {self.check_interval_minutes} minute(s)")
        
        # Schedule the job based on configuration
        if self.check_interval_minutes == 1:
            schedule.every().minute.do(self.process_headlines_job)
        else:
            schedule.every(self.check_interval_minutes).minutes.do(self.process_headlines_job)
        
        # Run once immediately
        logger.info("🔄 Running initial check...")
        self.process_headlines_job()
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)  # Check every second for scheduled jobs
        except KeyboardInterrupt:
            logger.info("🛑 Worker stopped by user")

def main():
    """
    Main entry point for the article generation worker.
    """
    try:
        worker = NewsArticleGenerationWorker()
        logger.info("📰 Article generation worker initialized successfully, starting simple worker...")
        worker.start_simple_worker()
    except KeyboardInterrupt:
        logger.info("🛑 Article generation worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Article generation worker failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main()