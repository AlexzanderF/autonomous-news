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

from celery_config import celery_app
from .shared import (
    get_genai_client,
    load_prompt,
    logger,
    SEARCH_PHRASES_MODEL_NAME,
    THUMBNAIL_PICKER_MODEL_NAME,
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
        
        # Search for an appropriate image
        wikimedia = WikimediaService()
        images = wikimedia.search_images(search_phrases)
        logger.info(f"Total images fetched for article ID {article_id}: {len(images)}")
        
        if not images:
            logger.warning(f"No images found with search phrases: {search_phrases}")
            return {
                'status': 'error',
                'message': f"No images found with search phrases: {search_phrases}"
            }

        thumbnail_title = pick_thumbnail_with_llm(article.title, article.content, images)
        if not thumbnail_title:
            logger.warning("Error picking thumbnail with LLM")
            return {
                'status': 'error',
                'message': "Error picking thumbnail with LLM"
            }

        thumbnail_url = None
        for image in images:
            if image['title'] == thumbnail_title:
                thumbnail_url = image['image_url']
                break

        if not thumbnail_url:
            logger.warning(f"Image with title {thumbnail_url} not found")
            return {
                'status': 'error',
                'message': f"Image with title {thumbnail_url} not found"
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

    input_data = [{
        'title': image['title'],
        'description': image['description'],
        'dimensions': image['dimensions'],
        'timestamp': image['timestamp']
    } for image in images]

    user_message = f"Article Title: {title}\nArticle Content: {content}\nImages:\n{json.dumps(input_data, indent=2)}"
    system_prompt = load_prompt('llm_prompts/pick_thumbnail_prompt.md')

    genai_client = get_genai_client()
    response = genai_client.models.generate_content(
        model=THUMBNAIL_PICKER_MODEL_NAME,
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type='application/json',
            thinking_config=genai.types.ThinkingConfig(thinking_budget=-1)
        )
    )

    response_text = response.text.strip()
    response_text = re.sub(r'^"(.*)"$', r'\1', response_text)

    try:
        return response_text
    except Exception as exc:
        logger.error(f"Unexpected error picking thumbnail: {exc}")
        return None