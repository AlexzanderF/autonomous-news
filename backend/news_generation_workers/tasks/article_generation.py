import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from google import genai
from celery import Task
from slugify import slugify
from sqlalchemy.orm import Session
import sys
from pathlib import Path
from .thumbnail_picker import add_thumbnail_to_article

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from dto import GeneratedArticleDTO, ArticleLLMResponseSchema
from db import Article, Category, get_database_session

from celery_config import celery_app
from .shared import (
    get_genai_client,
    load_prompt,
    logger,
    ARTICLE_GENERATION_MODEL_NAME,
    clean_json_response,
    ARTICLE_GENERATION_THINKING_BUDGET,
    ARTICLE_GENERATION_TEMPERATURE,
)

# ============================================================================
# Article Generation Task
# ============================================================================

@celery_app.task(bind=True, name='news_generation_workers.tasks.article_generation.generate_article_from_headline')
def generate_article_from_headline(self: Task, title: str, category: str) -> Dict[str, Any]:
    """
    Generate a full news article from a headline using Gemini with search/grounding.
    This task is queued automatically when headlines are selected.
    """
    try:
        logger.info(f"Generating article for headline: {title[:50]}...")

        if not title:
            logger.warning("Empty title received, skipping article generation")
            return {
                'status': 'error',
                'message': 'Empty title provided'
            }

        # Load the article generation prompt
        article_prompt_template = load_prompt('llm_prompts/generate_news_article_prompt.md')
        article_prompt = article_prompt_template.replace('{Topic Placeholder}', title)

        # Generate article using Gemini with search grounding
        genai_client = get_genai_client()
        response = genai_client.models.generate_content(
            contents=article_prompt,
            model=ARTICLE_GENERATION_MODEL_NAME,
            config=genai.types.GenerateContentConfig(
                temperature=ARTICLE_GENERATION_TEMPERATURE,
                tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())],
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=ARTICLE_GENERATION_THINKING_BUDGET
                )
            )
        )

        if not response or not response.text:
            logger.error(f"Empty response from Gemini for headline: {title}")
            return {
                'status': 'error',
                'message': 'Empty response from LLM'
            }

        # Parse the structured response
        try:
            cleaned_json = clean_json_response(response.text)
            article_data = ArticleLLMResponseSchema.model_validate_json(cleaned_json)
        except Exception as e:
            logger.error(f"Failed to parse article response: {e}")
            logger.error(f"Raw response: {response.text}")
            return {
                'status': 'error',
                'message': f'Failed to parse LLM response: {str(e)}'
            }
        article_content = article_data.content.strip()
        article_excerpt = article_data.excerpt.strip()
        sentiment_score = article_data.sentiment_score

        # Create GeneratedArticle object
        generated_article = GeneratedArticleDTO(
            title=title,
            category=category,
            content=article_content,
            excerpt=article_excerpt,
            sentiment_score=sentiment_score,
            generated_at=datetime.now(timezone.utc),
            status="draft"
        )

        logger.info(f"Successfully generated article for: {title[:50]}... (Length: {len(article_content)} chars)")

        # Store the article in the database
        article_id = store_generated_article(generated_article)
        if article_id:

            # Queue thumbnail selection task
            try:
                add_thumbnail_to_article.delay(article_id)
                logger.info(f"Queued thumbnail selection task for article ID: {article_id}")
            except Exception as thumbnail_exc:
                logger.warning(f"Failed to queue thumbnail task for article ID {article_id}: {thumbnail_exc}")

            return {
                'status': 'success',
                'title': title,
                'category': category,
                'content_length': len(article_content)
            }
        else:
            logger.error(f"Failed to store article: {title[:50]}...")
            return {
                'status': 'error',
                'message': 'Failed to store article in database'
            }

    except Exception as exc:
        logger.error(f"Error generating article for headline '{title}': {exc}")
        return {
            'status': 'error',
            'message': str(exc)
        }


# ============================================================================
# Helper Functions
# ============================================================================



def store_generated_article(article: GeneratedArticleDTO) -> Optional[int]:
    """Store the generated article in PostgreSQL database. Returns ID on success."""
    db = None
    try:
        db = get_database_session()

        # Get or create category
        category = get_or_create_category(db, article.category)

        # Generate unique slug
        slug = generate_unique_slug(db, article.title)

        # Create the Article record
        db_article = Article(
            title=article.title,
            slug=slug,
            content=article.content,
            excerpt=article.excerpt,
            sentiment_score=article.sentiment_score,
            ai_model_used=ARTICLE_GENERATION_MODEL_NAME,
            status=article.status,
            created_at=article.generated_at,
            updated_at=article.generated_at
        )

        # Add the article to the session
        db.add(db_article)
        db.commit()
        db.refresh(db_article)

        # Associate with category
        db_article.categories.append(category)

        db.commit()

        logger.info(f"Stored article in database: {article.title[:50]}... (ID: {db_article.id})")
        
        return db_article.id

    except Exception as exc:
        if db:
            db.rollback()
        logger.error(f"Failed to store article '{article.title}' in database: {exc}")
        return None

    finally:
        if db:
            db.close()


def get_or_create_category(db: Session, category_name: str) -> Category:
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


def generate_unique_slug(db: Session, title: str) -> str:
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

