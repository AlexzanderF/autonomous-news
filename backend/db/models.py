from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, Boolean, 
    ForeignKey, Table, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID

# Database base class
Base = declarative_base()

# Association table for article-category many-to-many relationship
article_categories = Table(
    'article_categories',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# Association table for article-source many-to-many relationship
article_sources = Table(
    'article_sources',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    Column('source_id', Integer, ForeignKey('sources.id'), primary_key=True)
)

class Category(Base):
    """
    News categories (e.g., Politics, Technology, Sports).
    Used to organize articles into logical groups.
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    
    # Relationships
    articles = relationship('Article', secondary=article_categories, back_populates='categories')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Source(Base):
    """
    Sources represent websites that Gemini used during search/grounding
    to generate article content. Multiple sources can be associated with each article.
    """
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, unique=True)  # Full URL of the source
    domain = Column(String(100), nullable=False)  # Extract domain for easier querying
    
    # Relationships
    articles = relationship('Article', secondary=article_sources, back_populates='sources')

    def __repr__(self):
        return f"<Source(id={self.id}, domain='{self.domain}', url='{self.url[:50]}...')>"

class Article(Base):
    """
    Main article model containing generated news content.
    
    This model stores:
    - Article content and metadata
    - SEO optimization fields
    - Source attribution
    - AI generation metadata
    - Full-text search capabilities
    - Relationships to categories, and sources
    """
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False, unique=True)
    excerpt = Column(Text, nullable=True)  # Short description/summary
    content = Column(Text, nullable=False)  # Generated article content
    thumbnail_url = Column(String(500), nullable=True)  # Local filename (e.g., 'article_123_abc.jpg')
    thumbnail_original_url = Column(String(500), nullable=True)  # Original provider URL (Freepik, Pexels, etc.)
    sentiment_score = Column(Integer, nullable=False, default=0, server_default='0')  # Sentiment score (0-100)
    
    # SEO and metadata
    # meta_title = Column(String(60), nullable=True)  # SEO title
    # meta_description = Column(String(160), nullable=True)  # SEO description
    
    # Article status and workflow
    status = Column(String(20), default='published')  # draft, published, archived
    
    # AI generation metadata
    ai_model_used = Column(String(50), nullable=True)
    
    # Full-text search
    # search_vector = Column(TSVECTOR)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sources = relationship('Source', secondary=article_sources, back_populates='articles')
    categories = relationship('Category', secondary=article_categories, back_populates='articles')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_articles_published_at', 'published_at'),
        # Index('idx_articles_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_articles_slug', 'slug'),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', slug='{self.slug}')>"

    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == 'published'

    @property
    def category_names(self):
        """Get list of category names for this article."""
        return [category.name for category in self.categories]

