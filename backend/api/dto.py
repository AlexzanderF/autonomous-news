from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, computed_field


class CategoryDTO(BaseModel):
    """DTO for article category."""
    id: int
    name: str

    class Config:
        from_attributes = True


class SourceDTO(BaseModel):
    """DTO for article source."""
    id: int
    url: str
    domain: str

    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    """DTO for full article response."""
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    thumbnail: Optional[str] = None  # Uses model's computed property with fallback
    thumbnail_attribution: Optional[dict] = None  # Thumbnail attribution as dict: {license, license_url, author, source}
    status: str
    article_type: str  # 'generated_news' or 'editorial'
    is_featured: bool = False
    created_at: datetime
    updated_at: datetime
    published_at: datetime
    categories: List[CategoryDTO] = []
    # LLM metadata fields (populated from llm_metadata relationship)
    ai_model_used: Optional[str] = None
    sentiment_score: Optional[int] = None
    sources: List[SourceDTO] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_llm(cls, article):
        """Create response from Article ORM object, flattening llm_metadata."""
        data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'excerpt': article.excerpt,
            'content': article.content,
            'thumbnail': article.thumbnail,
            'thumbnail_attribution': article.thumbnail_attribution,  # JSONB auto-deserializes to dict
            'status': article.status,
            'article_type': article.article_type.value if article.article_type else 'generated_news',
            'is_featured': article.is_featured,
            'created_at': article.created_at,
            'updated_at': article.updated_at,
            'published_at': article.published_at,
            'categories': article.categories,
        }
        if article.llm_metadata:
            data['ai_model_used'] = article.llm_metadata.ai_model_used
            data['sentiment_score'] = article.llm_metadata.sentiment_score
            data['sources'] = article.llm_metadata.sources
        return cls(**data)


class ArticleListItemDTO(BaseModel):
    """
    Lightweight DTO for article lists (e.g., homepage).
    Excludes full content to reduce payload size.
    """
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    thumbnail: Optional[str] = None  # Uses model's computed property with fallback
    published_at: datetime
    categories: List[CategoryDTO] = []
    # LLM metadata fields (populated from llm_metadata relationship)
    sentiment_score: Optional[int] = None
    is_featured: bool = False

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_llm(cls, article):
        """Create response from Article ORM object, flattening llm_metadata."""
        data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'excerpt': article.excerpt,
            'thumbnail': article.thumbnail,
            'published_at': article.published_at,
            'categories': article.categories,
            'is_featured': article.is_featured,
        }
        if article.llm_metadata:
            data['sentiment_score'] = article.llm_metadata.sentiment_score
        return cls(**data)


class PaginatedArticlesResponse(BaseModel):
    """
    Response DTO for paginated articles using cursor-based pagination.
    
    Cursor-based pagination provides better performance and consistency:
    - Uses primary key (ID) for efficient lookups
    - No offset calculations needed
    - Consistent results even when new items are added
    """
    items: List[ArticleListItemDTO]
    has_more: bool = Field(..., description="Whether there are more items to load")
    next_cursor: Optional[int] = Field(None, description="Cursor for next page (ID of last item)")
    
    # Legacy fields for compatibility (not used in cursor-based pagination)
    page: int = Field(1, description="Page number (deprecated, always 1)")
    page_size: int = Field(..., description="Number of items returned")
    total_pages: int = Field(0, description="Total pages (deprecated, always 0)")
