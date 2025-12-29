from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
import sys
import os

# Add parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db import Article, Category, ArticleType, ArticleLLMMetadata, get_db
from api.dto import ArticleResponse, ArticleListItemDTO, PaginatedArticlesResponse
from api.enum import SortField, SortOrder

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=PaginatedArticlesResponse)
def get_articles(
    cursor: Optional[int] = Query(None, description="Cursor for pagination (article ID)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    sort_field: SortField = Query(SortField.id, description="Field to sort by"),
    sort_direction: SortOrder = Query(SortOrder.desc, description="Sort direction (asc or desc)"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    article_type: Optional[str] = Query(None, description="Filter by article type: 'news' or 'editorial'"),
    db: Session = Depends(get_db)
):
    """
    Get published articles with cursor-based pagination and flexible sorting.
    Supports sorting by multiple fields in ascending or descending order.

    Args:
        cursor: Article ID to start from (exclusive). Omit for first page.
        limit: Number of items to return (default: 10, max: 100)
        sort_field: Field to sort by (id, published_at, title, created_at)
        sort_direction: Sort direction (asc or desc)
        category: Optional category filter
        article_type: Optional filter by type ('news' for generated, 'editorial' for handwritten)
        db: Database session (injected)
    
    Returns:
        Paginated list of articles with cursor for next page
    """
    # Build base query
    query = db.query(Article).options(
        joinedload(Article.categories),
        joinedload(Article.llm_metadata)
    ).filter(
        Article.status == 'published'
    )
    
    # Apply category filter if provided
    if category:
        query = query.join(Article.categories).filter(Category.name == category)
    
    # Apply article type filter if provided
    if article_type:
        if article_type.lower() == 'news':
            query = query.filter(Article.article_type == ArticleType.GENERATED_NEWS)
        elif article_type.lower() == 'editorial':
            query = query.filter(Article.article_type == ArticleType.EDITORIAL)
    
    # Apply cursor-based pagination
    if cursor is not None:
        if sort_direction == SortOrder.desc:
            query = query.filter(Article.id < cursor)
        else:
            query = query.filter(Article.id > cursor)
    
    # Build sort expression based on field and direction
    sort_column = getattr(Article, sort_field.value)
    
    if sort_direction == SortOrder.desc:
        primary_sort = desc(sort_column)
        secondary_sort = desc(Article.id)
    else:
        primary_sort = asc(sort_column)
        secondary_sort = asc(Article.id)
    
    # Apply sorting (primary field + ID for consistency)
    if sort_field == SortField.id:
        query = query.order_by(primary_sort)
    else:
        query = query.order_by(primary_sort, secondary_sort)
    
    # Fetch limit + 1 to check if there are more items
    articles = query.limit(limit + 1).all()
    
    has_more = len(articles) > limit
    
    # Remove the extra item if we fetched limit + 1
    if has_more:
        articles = articles[:limit]
    
    # Get next cursor (ID of last item) if there are more items
    next_cursor = articles[-1].id if articles and has_more else None
    
    # Convert to DTOs with flattened LLM metadata
    items = [ArticleListItemDTO.from_orm_with_llm(article) for article in articles]
    
    return PaginatedArticlesResponse(
        items=items,
        has_more=has_more,
        next_cursor=next_cursor,
        page_size=limit,
    )


@router.get("/{slug}", response_model=ArticleResponse)
def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a single article by its slug.
    
    Args:
        slug: Article slug (URL-friendly identifier)
        db: Database session (injected)
    
    Returns:
        Full article with content, categories, and sources
    """
    article = db.query(Article).options(
        joinedload(Article.categories),
        joinedload(Article.llm_metadata).joinedload(ArticleLLMMetadata.sources)
    ).filter(
        Article.slug == slug,
        Article.status == 'published'
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return ArticleResponse.from_orm_with_llm(article)
