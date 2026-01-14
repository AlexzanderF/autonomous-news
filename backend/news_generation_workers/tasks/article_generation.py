import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from celery import Task
import json
from slugify import slugify
from sqlalchemy.orm import Session
import sys
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_tavily import TavilySearch

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from dto import GeneratedArticleDTO
from db import Article, Category, ArticleLLMMetadata, get_database_session

from .thumbnail_picker import add_thumbnail_to_article
from celery_config import celery_app
from .shared import (
    get_llm,
    load_prompt,
    logger,
    ARTICLE_GENERATION_MODEL_NAME,
    clean_json_response,
    ARTICLE_GENERATION_TEMPERATURE,
    ARTICLE_GENERATION_THINKING_BUDGET,
    ARTICLE_METADATA_MODEL_NAME,
    TAVILY_API_KEY,
)

TAVILY_MAX_RESULTS = 20
TAVILY_DAYS = 3
MAX_RETRIES = 2
EMPTY_RESPONSE_RETRY_DELAY = 30  # Retry delay for empty responses (Gemini internal errors)

# ============================================================================
# Article Generation Task
# ============================================================================

def _generate_with_gemini_search(title: str, system_prompt: str) -> str:
    """
    Generate article content using Gemini with built-in Google Search grounding.
    Used for regular (non-featured) articles.
    """
    llm = get_llm(
        model_name=ARTICLE_GENERATION_MODEL_NAME,
        temperature=ARTICLE_GENERATION_TEMPERATURE,
        thinking_budget=ARTICLE_GENERATION_THINKING_BUDGET,
        max_retries=MAX_RETRIES,
    )
    # Bind Google Search tool for real-time search grounding
    llm_with_search = llm.bind_tools([{"google_search": {}}])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", "Generate an article for the following headline: {title}"),
    ])
    
    chain = prompt | llm_with_search | StrOutputParser()
    return chain.invoke({
        "system_prompt": system_prompt,
        "title": title,
    })


def _generate_with_tavily(title: str, system_prompt: str) -> str:
    """
    Generate article content using Tavily search + Claude (Anthropic).
    Used for featured articles for higher quality output.
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY environment variable is required for featured article generation")
    
    # Step 1: Search for context using Tavily
    tavily = TavilySearch(
        api_key=TAVILY_API_KEY,
        topic="news",
        max_results=TAVILY_MAX_RESULTS,
        days=TAVILY_DAYS
    )
    
    logger.info(f"Searching for context with Tavily for headline: {title}")
    search_results = tavily.invoke(title)
    
    # Format search results as context
    if isinstance(search_results.get('results'), list):
        context = "\n\n".join([
            f"Source: {r.get('url', 'Unknown')}\n{r.get('content', '')}" 
            for r in search_results['results']
        ])
        result_count = len(search_results['results'])
    else:
        context = str(search_results)
        result_count = 1
    
    logger.info(f"Tavily search returned {result_count} results")
    
    # Step 2: Generate article with Claude using search context
    llm = get_llm(
        model_name='claude-haiku-4-5',
        temperature=ARTICLE_GENERATION_TEMPERATURE,
        max_retries=MAX_RETRIES,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", "Generate an article for the following headline: {title}\n\nResearch context from web search:\n{context}"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "system_prompt": system_prompt,
        "title": title,
        "context": context,
    })


@celery_app.task(
    bind=True,
    name='news_generation_workers.tasks.article_generation.generate_article_from_headline',
    max_retries=MAX_RETRIES,
    default_retry_delay=EMPTY_RESPONSE_RETRY_DELAY,
)
def generate_article_from_headline(self: Task, title: str, category: str, is_featured: bool = False) -> Dict[str, Any]:
    """
    Generate a full news article from a headline.
    This task is queued automatically when headlines are selected.
    """
    try:
        logger.info(f"Generating {'featured ' if is_featured else ''}article for headline: {title[:50]}...")

        if not title:
            logger.warning("Empty title received, skipping article generation")
            raise ValueError("Empty title provided")

        # Load the article generation prompt
        system_prompt = load_prompt('llm_prompts/generate_news_article_prompt.md')
        
        # Choose generation method based on featured status
        if is_featured:
            logger.info("Using Tavily + Claude for featured article")
            article_content = _generate_with_tavily(title, system_prompt)
        else:
            logger.info("Using Gemini + Google Search for regular article")
            article_content = _generate_with_gemini_search(title, system_prompt)

        # Handle empty responses
        if not article_content or not article_content.strip():
            logger.warning(f"Empty Article content response from LLM for headline: {title}")
            raise self.retry(
                exc=RuntimeError("Empty Article content response from LLM"),
                kwargs={'title': title, 'category': category, 'is_featured': is_featured},
                countdown=EMPTY_RESPONSE_RETRY_DELAY
            )
        
        article_content = article_content.strip()

        # Generate article metadata using LangChain
        # Note: Using single human message since some models (like Gemma) don't support system instructions
        instructions = load_prompt('llm_prompts/article_metadata_prompt.md')
        
        llm = get_llm(model_name=ARTICLE_METADATA_MODEL_NAME)
        
        # Create prompt template with combined instructions and content
        prompt = ChatPromptTemplate.from_messages([
            ("human", "{instructions}\n\nArticle Title: {title}\nArticle Content:\n{content}"),
        ])
        
        # Create and invoke the chain
        chain = prompt | llm
        metadata_response = chain.invoke({
            "instructions": instructions,
            "title": title,
            "content": article_content,
        })

        if not metadata_response or not metadata_response.content:
            logger.error(f"Empty excerpt and key points response from LLM for headline: {title}")
            raise RuntimeError("Empty excerpt and key points response from LLM")

        # Parse the structured response
        try:
            cleaned_json = clean_json_response(metadata_response.content)
            parsed_metadata = json.loads(cleaned_json)
            article_excerpt = parsed_metadata['excerpt'].strip()
            key_points = parsed_metadata['key_points']
        except Exception as e:
            logger.error(f"Failed to parse article metadata response as JSON: {e}. Raw response: {metadata_response.content}")
            raise ValueError(f"Failed to parse article metadata response: {str(e)}")

        # Create GeneratedArticle object
        generated_article = GeneratedArticleDTO(
            title=title,
            category=category,
            content=article_content,
            excerpt=article_excerpt,
            key_points=key_points,
            generated_at=datetime.now(timezone.utc),
            status="draft",
            is_featured=is_featured
        )

        logger.info(f"Successfully generated article for: {title[:50]}... (Length: {len(article_content)} chars)")

        # Store the article in the database
        article_id = store_generated_article(generated_article)

        if not article_id:
            logger.error(f"Missing article ID after storing article: {title[:50]}...")
            raise ValueError("Missing article ID after storing article")

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

    except Exception as exc:
        logger.error(f"Error generating article for headline '{title}': {exc}")
        raise ValueError(f"Error generating article for headline '{title}': {exc}")


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
            status=article.status,
            is_featured=article.is_featured,
            created_at=article.generated_at,
            updated_at=article.generated_at
        )

        # Add the article to the session
        db.add(db_article)
        db.commit()
        db.refresh(db_article)

        # Associate with category
        db_article.categories.append(category)
        
        # Create LLM metadata record
        llm_metadata = ArticleLLMMetadata(
            article_id=db_article.id,
            ai_model_used=ARTICLE_GENERATION_MODEL_NAME,
            key_points=article.key_points
        )
        db.add(llm_metadata)

        db.commit()

        logger.info(f"Stored article in database: {article.title[:50]}... (ID: {db_article.id})")
        
        return db_article.id

    except Exception as exc:
        if db:
            db.rollback()
        logger.error(f"Failed to store article '{article.title}' in database: {exc}")
        raise exc

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

