from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class ScrapedArticleDTO(BaseModel):
    title: str
    source: str
    date: datetime
    link: HttpUrl
    short_description: Optional[str] = None
    extracted_from: str  # Where the headline was extracted from (e.g., "Google News", "Reuters RSS", etc.)

class ProcessedHeadlineDTO(BaseModel):
    title: str
    category: str
    is_featured: bool = False

class HeadlinePickerResponse(BaseModel):
    """Structured response from the LLM for headline selection."""
    headlines: List[ProcessedHeadlineDTO]

class GeneratedArticleDTO(BaseModel):
    title: str
    category: str
    content: str
    excerpt: Optional[str] = None
    key_points: Optional[List[str]] = None
    generated_at: datetime
    status: str = "draft"
    source_urls: Optional[List[str]] = []
    is_featured: bool = False


class ThumbnailPickerResponse(BaseModel):
    """Structured response from the LLM for thumbnail selection."""
    id: int  # The selected image ID from the candidates list