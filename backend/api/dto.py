from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

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
    """DTO for article response."""
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    thumbnail_url: Optional[str] = None
    status: str
    ai_model_used: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: datetime
    categories: List[CategoryDTO] = []
    sources: List[SourceDTO] = []
    sentiment_score: Optional[int] = None

    class Config:
        from_attributes = True


class ArticleListItemDTO(BaseModel):
    """
    Lightweight DTO for article lists (e.g., homepage).
    Excludes full content to reduce payload size.
    """
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    thumbnail_url: Optional[str] = None
    published_at: datetime
    categories: List[CategoryDTO] = []
    sentiment_score: int

    class Config:
        from_attributes = True


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

