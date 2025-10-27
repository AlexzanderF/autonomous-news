"""Shared utilities and configuration for Celery tasks."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import redis
from google import genai
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from db.models import Article, Category, Base

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('celery_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_LAST_RUN_KEY = 'news:worker:last_run_timestamp'

# Database configuration
DB_URL = os.getenv('DB_URL')
if not DB_URL:
    raise ValueError("DB_URL environment variable is required")

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# LLM configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY environment variable is required")

LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'gemini-2.5-flash')
if not LLM_MODEL_NAME:
    raise ValueError("LLM_MODEL_NAME environment variable is required")

# Paths
WORKER_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# Client Factories
# ============================================================================

def get_redis_client() -> redis.Redis:
    """Create and return a Redis client."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD if REDIS_PASSWORD else None,
        decode_responses=True
    )


def get_genai_client() -> genai.Client:
    """Create and return a Google GenAI client."""
    return genai.Client(api_key=LLM_API_KEY)


def get_database_session() -> Session:
    """Create and return a new database session."""
    return SessionLocal()


# ============================================================================
# Utility Functions
# ============================================================================

def load_prompt(filename: str) -> str:
    """Load a prompt template from a markdown file."""
    prompt_path = WORKER_DIR / filename
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

