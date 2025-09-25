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
    category: Optional[str] = None
    explanation: str = ""

class GeneratedArticleDTO(BaseModel):
    title: str
    category: str
    content: str
    generated_at: datetime
    status: str = "draft"
    source_urls: Optional[List[str]] = []