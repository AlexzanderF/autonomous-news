import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from celery import Task
import sys
from pathlib import Path
from google import genai
import json
import re

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from db import get_database_session, Article
from services.wikimedia_service import WikimediaService
from services.pexels_service import PexelsService
from services.freepik_service import FreepikService

from celery_config import celery_app
from .shared import (
    get_genai_client,
    load_prompt,
    logger,
    SEARCH_PHRASES_MODEL_NAME,
    THUMBNAIL_PICKER_MODEL_NAME,
    THUMBNAIL_PICKER_THINKING_BUDGET,
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
            logger.error(f"Article with ID {article_id} not found")
            return {
                'status': 'error',
                'message': f'Article with ID {article_id} not found'
            }
        
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
            logger.warning(f"No images found with search phrases: {search_phrases}")
            return {
                'status': 'error',
                'message': f"No images found with search phrases: {search_phrases}"
            }

        thumbnail_id_str = pick_thumbnail_with_llm(article.title, article.content, images)
        if not thumbnail_id_str:
            logger.warning("Error picking thumbnail with LLM")
            return {
                'status': 'error',
                'message': "Error picking thumbnail with LLM"
            }

        thumbnail_url = None
        try:
            thumbnail_idx = int(thumbnail_id_str)
            if 0 <= thumbnail_idx < len(images):
                thumbnail_url = images[thumbnail_idx]['image_url']
            else:
                logger.warning(f"Returned ID {thumbnail_idx} is out of bounds (0-{len(images)-1})")
        except ValueError:
            logger.warning(f"Returned ID '{thumbnail_id_str}' is not an integer")

        if not thumbnail_url:
            logger.warning(f"Image with ID {thumbnail_id_str} not found or invalid")
            return {
                'status': 'error',
                'message': f"Image with ID {thumbnail_id_str} not found or invalid"
            }
        
        # Update the article with the thumbnail URL and mark as published
        article.thumbnail_url = thumbnail_url
        article.updated_at = datetime.now(timezone.utc)
        article.status = 'published'
        article.published_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(article)
        
        logger.info(f"Successfully added thumbnail to article ID {article_id}: {thumbnail_url}")
        
        return {
            'status': 'success',
            'article_id': article_id,
            'thumbnail_url': thumbnail_url
        }
        
    except Exception as exc:
        logger.error(f"Error adding thumbnail to article ID {article_id}: {exc}")
        return {
            'status': 'error',
            'message': str(exc)
        }
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

def pick_thumbnail_with_llm(title: str, content: str, images: List[Dict[str, Any]]) -> Optional[str]:
    """
    Pick a thumbnail from a list of images using LLM.
    """

    input_data = []
    for idx, image in enumerate(images):
        line = f"ID: {idx} Title: {image['title']} | Dimension: {image['dimensions']} | Desc: {image['description']}"
        input_data.append(line)

    user_message = f"Article Title: {title}\nArticle Content: {content}\nImages candidates:\n{"n".join(input_data)}"
    system_prompt = load_prompt('llm_prompts/pick_thumbnail_prompt.md')

    genai_client = get_genai_client()
    response = genai_client.models.generate_content(
        model=THUMBNAIL_PICKER_MODEL_NAME,
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type='application/json',
            temperature=THUMBNAIL_PICKER_TEMPERATURE,
            thinking_config=genai.types.ThinkingConfig(thinking_budget=THUMBNAIL_PICKER_THINKING_BUDGET)
        )
    )

    response_text = response.text.strip()
    match = re.search(r'\d+', response_text)

    try:
        if match:
            return match.group(0)

        logger.warning(f"No integer ID found in LLM response: {response_text}")
        return None
    except Exception as exc:
        logger.error(f"Unexpected error picking thumbnail: {exc}")
        return None