from datetime import datetime
from pydantic import BaseModel, HttpUrl

class ScrapedArticleDTO(BaseModel):
    title: str
    source: str
    date: datetime
    link: HttpUrl
    short_description: str | None = None
    extracted_from: str  # Where the headline was extracted from (e.g., "Google News", "Reuters RSS", etc.)