"""Shared utilities and configuration for Celery tasks."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import redis
from google import genai
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
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

# LLM configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY environment variable is required")

HEADLINES_PICKER_MODEL_NAME = os.getenv('HEADLINES_PICKER_MODEL_NAME', 'gemini-2.5-flash')
ARTICLE_GENERATION_MODEL_NAME = os.getenv('ARTICLE_GENERATION_MODEL_NAME', 'gemini-2.5-flash')
ARTICLE_METADATA_MODEL_NAME = os.getenv('ARTICLE_METADATA_MODEL_NAME', 'gemma-3-27b-it')
# Thumbnail picker models
SEARCH_PHRASES_MODEL_NAME = os.getenv('SEARCH_PHRASES_MODEL_NAME', 'gemma-3-27b-it')
THUMBNAIL_PICKER_MODEL_NAME = os.getenv('THUMBNAIL_PICKER_MODEL_NAME', 'gemini-flash-lite-latest')

# Thinking Budgets
HEADLINES_PICKER_THINKING_BUDGET = int(os.getenv('HEADLINES_PICKER_THINKING_BUDGET', 0))
ARTICLE_GENERATION_THINKING_BUDGET = int(os.getenv('ARTICLE_GENERATION_THINKING_BUDGET', 0))
THUMBNAIL_PICKER_THINKING_BUDGET = int(os.getenv('THUMBNAIL_PICKER_THINKING_BUDGET', 0))

# Temperatures
HEADLINES_PICKER_TEMPERATURE = float(os.getenv('HEADLINES_PICKER_TEMPERATURE', 1.0))
ARTICLE_GENERATION_TEMPERATURE = float(os.getenv('ARTICLE_GENERATION_TEMPERATURE', 1.0))
THUMBNAIL_PICKER_TEMPERATURE = float(os.getenv('THUMBNAIL_PICKER_TEMPERATURE', 1.0))

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


def clean_json_response(response_text: str) -> str:
    """
    Clean up LLM response text that might contain markdown code blocks.
    Extracts JSON content from ```json ... ``` or ``` ... ``` blocks.
    """
    if not response_text:
        return ""
        
    cleaned_text = response_text.strip()
    
    # Check for markdown code blocks
    if '```' in cleaned_text:
        # Try to find content between ```json and ``` or just ``` and ```
        # This regex looks for ```(optional language)\n(content)\n```
        import re
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', cleaned_text, re.DOTALL)
        if match:
            cleaned_text = match.group(1).strip()
    
    return cleaned_text
