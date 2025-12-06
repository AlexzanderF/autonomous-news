import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from celery import Task
from sqlalchemy.orm import Session
import sys
from pathlib import Path
from google import genai
import json
import os
import re

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from db import get_database_session, Article

from celery_config import celery_app
from .shared import (
    get_genai_client,
    load_prompt,
    logger,
    SEARCH_PHRASES_MODEL_NAME,
    THUMBNAIL_PICKER_MODEL_NAME,
)

# ============================================================================
# Image Selection Task
# ============================================================================

WIKIMEDIA_API_BASE = "https://commons.wikimedia.org/w/api.php"
WIKIMEDIA_IMAGE_URL_TEMPLATE = "https://commons.wikimedia.org/wiki/Special:FilePath/{filename}"
WIKIMEDIA_HEADERS = {
    'User-Agent': (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/svg+xml',
    'image/svg'
}


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
        
        # Search for an appropriate image
        images = get_wikimedia_images(search_phrases)
        
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

def get_wikimedia_images(search_phrases: List[str]) -> List[Dict[str, Any]]:
    """
    Search Wikimedia Commons for an appropriate image based on keywords.
    
    Args:
        search_phrases: List of search phrases to search for
        
    Returns:
        List of dictionaries containing the title and image URL of the images found
    """

    fetched_images = []

    for search_phrase in search_phrases:
        try:
            # Wikimedia Commons API request
            params = {
                'action': 'query',
                'format': 'json',
                'generator': 'search',
                'gsrsearch': f"{search_phrase} filetype:bitmap",
                'gsrnamespace': 6,  # File namespace (media)
                'gsrlimit': 10,  # Get top 10 results
                'prop': 'imageinfo',
                'iiprop': 'url|mime|size|mediatype|extmetadata'
            }
            
            response = requests.get(WIKIMEDIA_API_BASE, params=params, headers=WIKIMEDIA_HEADERS, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'query' not in data or 'pages' not in data['query']:
                continue
            
            search_results = data['query']['pages'].values()
            
            if not search_results:
                continue
            
            for result in search_results:
                title = result.get('title')
                image_info = result.get('imageinfo', [{}])[0]
                image_url = image_info.get('url')
                description = image_info.get('extmetadata', {}).get('ImageDescription', {}).get('value')
                width = image_info.get('width')
                height = image_info.get('height')

                if title and image_url: 
                    fetched_images.append({
                        'title': title,
                        'description': description if description else None,
                        'image_url': image_url,
                        'dimensions': f"{width}x{height}" if width and height else None,
                    })
            
        except requests.RequestException as exc:
            logger.error(f"Error querying Wikimedia Commons API: {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error finding image: {exc}")

    return fetched_images

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
        'description': image['description']
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