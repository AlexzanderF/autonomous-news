import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from celery import Task
import sys
from pathlib import Path
from google import genai
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from news_generation_workers.dto import ThumbnailPickerResponse
from db import get_database_session, Article
from services.wikimedia_service import WikimediaService
from services.pexels_service import PexelsService
from services.freepik_service import FreepikService
from services.image_storage_service import ImageStorageService

from celery_config import celery_app
from .shared import (
    get_genai_client,
    load_prompt,
    logger,
    SEARCH_PHRASES_MODEL_NAME,
    THUMBNAIL_PICKER_MODEL_NAME,
    THUMBNAIL_PICKER_THINKING_BUDGET,
    THUMBNAIL_PICKER_THINKING_LEVEL,
    THUMBNAIL_PICKER_TEMPERATURE,
)


@celery_app.task(bind=True, name='news_generation_workers.tasks.thumbnail_picker.add_thumbnail_to_article')
def add_thumbnail_to_article(self: Task, article_id: int) -> Dict[str, Any]:
    """
    Add a thumbnail image to an article using Wikimedia Commons API.
    This task is queued automatically when articles are generated.
    """
    try:
        logger.info(f"Adding thumbnail to article ID: {article_id}")
        
        db = get_database_session()
        
        # Fetch the article
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise ValueError(f"Article with ID {article_id} not found")
        
        # Check if thumbnail already exists
        if article.thumbnail_url:
            logger.info(f"Article ID {article_id} already has a thumbnail: {article.thumbnail_url}")
            return {
                'status': 'success',
                'message': 'Article already has a thumbnail',
                'thumbnail_url': article.thumbnail_url
            }

        # Get search phrases based on article content
        search_phrases = get_search_phrases_with_llm(article.title, article.content)
        logger.info(f"Search phrases used for article ID {article_id}: {search_phrases}")
        
        images = []

        # Search for an appropriate image from Wikimedia
        try:
            wikimedia = WikimediaService()
            wikimedia_images = wikimedia.search_images_by_phrases_list(search_phrases, 15)
            images.extend(wikimedia_images)
            logger.info(f"Wikimedia images fetched for article ID {article_id}: {len(wikimedia_images)}")
        except Exception as exc:
            logger.warning(f"Failed to fetch Wikimedia images: {exc}")
        
        # Search for images from Pexels (if API key is available)
        try:
            pexels = PexelsService()
            pexels_images = pexels.search_images_by_phrases_list(search_phrases, 10, 'landscape')
            images.extend(pexels_images)
            logger.info(f"Pexels images fetched for article ID {article_id}: {len(pexels_images)}")
        except Exception as exc:
            logger.warning(f"Failed to fetch Pexels images: {exc}")
        
        # Search for images from Freepik (if API key is available)
        try:
            freepik = FreepikService()
            freepik_images = freepik.search_images_by_phrases_list(search_phrases, 10, 'landscape')
            images.extend(freepik_images)
            logger.info(f"Freepik images fetched for article ID {article_id}: {len(freepik_images)}")
        except Exception as exc:
            logger.warning(f"Failed to fetch Freepik images: {exc}")
        
        logger.info(f"Total images fetched for article ID {article_id}: {len(images)}")
        
        if not images:
            raise ValueError(f"No images found with search phrases: {search_phrases}")

        thumbnail_id = pick_thumbnail_with_llm(article.title, article.content, images)
        if thumbnail_id is None:
            raise ValueError("Error picking thumbnail with LLM")

        # Convert 1-based ID to 0-based index for array access
        thumbnail_idx = thumbnail_id - 1
        if 0 <= thumbnail_idx < len(images):
            provider_thumbnail_url = images[thumbnail_idx]['image_url']
        else:
            raise ValueError(f"Image with ID {thumbnail_id} not found or invalid")
        
        # Download and store the image locally to avoid 429 rate limits from providers
        image_storage = ImageStorageService()
        stored_filename = image_storage.download_and_store(article_id, provider_thumbnail_url)
        
        if not stored_filename:
            logger.warning(f"Failed to store image locally, falling back to provider URL: {provider_thumbnail_url}")
            stored_filename = provider_thumbnail_url  # Fallback to external URL
        else:
            logger.info(f"Image stored locally for article {article_id}: {stored_filename}")
        
        # Update the article with both the local filename and original provider URL
        article.thumbnail_url = stored_filename
        article.thumbnail_original_url = provider_thumbnail_url  # Store original for reference
        article.updated_at = datetime.now(timezone.utc)
        article.status = 'published'
        article.published_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(article)
        
        logger.info(f"Successfully added thumbnail to article ID {article_id}: {stored_filename}")
        
        return {
            'status': 'success',
            'article_id': article_id,
            'thumbnail_filename': stored_filename,
            'thumbnail_original_url': provider_thumbnail_url
        }
        
    except Exception as exc:
        logger.error(f"Error adding thumbnail to article ID {article_id}: {exc}")
        raise exc
    finally:
        if db:
            db.close()

# ============================================================================
# Helper Functions
# ============================================================================

def get_search_phrases_with_llm(title: str, content: str) -> List[str]:
    """
    Get search phrases for an article using LLM.
    """

    system_prompt = load_prompt('llm_prompts/extract_search_phrases_prompt.md')
    user_message = f"{system_prompt}\nArticle Title: {title}\nArticle Content: {content}"
    genai_client = get_genai_client()

    response = genai_client.models.generate_content(
        model=SEARCH_PHRASES_MODEL_NAME,
        contents=user_message,
    )

    response_text = response.text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse JSON response: {exc}. Raw output: {response_text[:200]}...")
        return []

def pick_thumbnail_with_llm(title: str, content: str, images: List[Dict[str, Any]]) -> Optional[int]:
    """
    Pick a thumbnail from a list of images using LLM with structured output.
    Returns the selected image ID as an integer, or None if selection fails.
    """
    # Use 1-based IDs for LLM (more intuitive for the model)
    max_valid_id = len(images)

    input_data = []
    for idx, image in enumerate(images, start=1):
        line = f"ID: {idx} Title: {image['title']} | Dimension: {image['dimensions']} | Desc: {image['description']}"
        input_data.append(line)

    user_message = f"Article Title: {title}\nArticle Content: {content}\nImages candidates:\n{"\n".join(input_data)}"
    system_prompt = load_prompt('llm_prompts/pick_thumbnail_prompt.md')

    genai_client = get_genai_client()
    
    try:
        response = genai_client.models.generate_content(
            model=THUMBNAIL_PICKER_MODEL_NAME,
            contents=user_message,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type='application/json',
                response_schema=ThumbnailPickerResponse,
                temperature=THUMBNAIL_PICKER_TEMPERATURE,
                thinking_config=genai.types.ThinkingConfig(thinking_budget=THUMBNAIL_PICKER_THINKING_BUDGET)
            )
        )

        # Parse the structured response using Pydantic
        parsed_response = ThumbnailPickerResponse.model_validate_json(response.text)
        thumbnail_id = parsed_response.id
        
        logger.info(f"LLM thumbnail picker selected ID: {thumbnail_id}")

        # Validate the ID is within bounds (1 to max_valid_id)
        if 1 <= thumbnail_id <= max_valid_id:
            return thumbnail_id
        else:
            logger.warning(f"LLM returned ID {thumbnail_id} is out of bounds (1-{max_valid_id})")
            return None
            
    except Exception as exc:
        logger.error(f"Error picking thumbnail with LLM: {exc}")
        return None