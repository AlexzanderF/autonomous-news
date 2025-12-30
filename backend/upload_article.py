#!/usr/bin/env python3
"""
Upload handwritten articles to the database.

Usage:
    python upload_article.py <path_to_markdown_file.md> [--category CATEGORY]

Example:
    python upload_article.py "Sample Title.md" --category "Economy"

The title is derived from the markdown filename (without .md extension).
The slug is generated from the title.
Excerpt and thumbnail columns are left NULL.
"""

import argparse
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from slugify import slugify
from sqlalchemy.orm import Session

from db import get_database_session, Article, Category, ArticleType


def get_or_create_category(db: Session, category_name: str) -> Category:
    """Get or create a category by name."""
    category = db.query(Category).filter(Category.name == category_name).first()
    if not category:
        category = Category(name=category_name)
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


def upload_article(file_path: Path, category_name: str = None) -> int:
    """
    Upload a markdown article to the database.
    
    Args:
        file_path: Path to the markdown file
        category_name: Optional category name
        
    Returns:
        The article ID
    """
    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.suffix.lower() == '.md':
        raise ValueError(f"File must be a markdown (.md) file: {file_path}")
    
    # Extract title from filename (without extension)
    title = file_path.stem
    
    # Read content
    content = file_path.read_text(encoding='utf-8')
    
    if not content.strip():
        raise ValueError(f"File is empty: {file_path}")
    
    # Generate slug from title
    db = None
    try:
        db = get_database_session()
        
        slug = generate_unique_slug(db, title)
        now = datetime.now(timezone.utc)
        
        # Generate thumbnail filename for manual upload
        thumbnail_filename = f"editorial_article_{uuid.uuid4()}.png"

        # Create the Article record
        article = Article(
            title=title,
            slug=slug,
            content=content,
            excerpt=None,
            thumbnail_url=thumbnail_filename,
            thumbnail_original_url=None,
            status='published',
            article_type=ArticleType.EDITORIAL,  # Handwritten articles are editorials
            created_at=now,
            updated_at=now,
            published_at=now
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        # Associate with category if provided
        if category_name:
            category = get_or_create_category(db, category_name)
            article.categories.append(category)
            db.commit()
        
        print(f"✅ Successfully uploaded article:")
        print(f"   ID: {article.id}")
        print(f"   Title: {article.title}")
        print(f"   Slug: {article.slug}")
        print(f"   Category: {category_name or 'None'}")
        print(f"   Content length: {len(content)} characters")
        print(f"")
        print(f"📷 Thumbnail filename: {thumbnail_filename}")
        print(f"   Use this filename when uploading your thumbnail image.")
        
        return article.id
        
    except Exception as exc:
        if db:
            db.rollback()
        raise exc
    finally:
        if db:
            db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Upload a handwritten markdown article to the database.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python upload_article.py "My Article Title.md"
    python upload_article.py "Economy Analysis.md" --category "Economy"
    python upload_article.py ./articles/tech-review.md --category "Technology"
        """
    )
    parser.add_argument(
        'file',
        type=Path,
        help='Path to the markdown file (title is derived from filename)'
    )
    parser.add_argument(
        '--category', '-c',
        type=str,
        default=None,
        help='Category name for the article (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        article_id = upload_article(args.file, args.category)
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to upload article: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
