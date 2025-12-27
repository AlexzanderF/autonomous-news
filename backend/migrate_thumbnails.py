#!/usr/bin/env python3
"""
Migration script to download and store existing article thumbnails locally.

This script finds all articles with thumbnail URLs that point to external providers
(Freepik, Pexels, Wikimedia, etc.) and downloads them to local storage, updating
the database with the local filename (e.g., 'article_123_abc.jpg').
The frontend constructs the full URL using the getThumbnailUrl() helper.

Usage:
    python migrate_thumbnails.py [--dry-run] [--limit N]
    
Options:
    --dry-run   Show what would be migrated without making changes
    --limit N   Only process N articles (useful for testing)
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent))

from db import get_database_session, Article
from services.image_storage_service import ImageStorageService

# Patterns that indicate an external provider URL
EXTERNAL_PATTERNS = [
    'freepik.com',
    'pexels.com',
    'wikimedia.org',
    'upload.wikimedia.org',
    'commons.wikimedia.org',
    'picsum.photos',
    # Add more as needed
]

def is_external_url(url: str) -> bool:
    """Check if a URL is from an external provider."""
    if not url:
        return False
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in EXTERNAL_PATTERNS)


def migrate_thumbnails(dry_run: bool = False, limit: int = None, hours: int = None):
    """
    Migrate external thumbnail URLs to locally stored images.
    
    Args:
        dry_run: If True, only show what would be done without making changes
        limit: Maximum number of articles to process
        hours: Only process articles from the last N hours
    """
    db = get_database_session()
    image_storage = ImageStorageService()
    
    try:
        # Build query
        query = db.query(Article).filter(
            Article.thumbnail_url.isnot(None),
            Article.status == 'published'
        )
        
        # Filter by time if specified
        if hours:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            query = query.filter(Article.published_at >= cutoff)
        
        # Order by most recent first
        query = query.order_by(Article.published_at.desc())
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        articles = query.all()
        
        # Filter to only external URLs
        articles_to_migrate = [
            a for a in articles 
            if is_external_url(a.thumbnail_url)
        ]
        
        print(f"Found {len(articles_to_migrate)} articles with external thumbnail URLs")
        
        if dry_run:
            print("\n[DRY RUN] Would migrate the following articles:")
            for article in articles_to_migrate:
                print(f"  - Article {article.id}: {article.title[:50]}...")
                print(f"    Current URL: {article.thumbnail_url[:80]}...")
            return
        
        # Process each article
        migrated = 0
        failed = 0
        
        for article in articles_to_migrate:
            print(f"\nProcessing article {article.id}: {article.title[:50]}...")
            
            original_url = article.thumbnail_url
            stored_filename = image_storage.download_and_store(article.id, original_url)
            
            if stored_filename:
                article.thumbnail_url = stored_filename
                article.updated_at = datetime.now(timezone.utc)
                db.commit()
                print(f"  ✓ Stored as: {stored_filename}")
                migrated += 1
            else:
                print(f"  ✗ Failed to download from: {original_url}")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"Migration complete!")
        print(f"  Migrated: {migrated}")
        print(f"  Failed: {failed}")
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate external thumbnail URLs to local storage"
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be migrated without making changes'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of articles to process'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Only process articles from the last N hours (default: 24)'
    )
    
    args = parser.parse_args()
    
    migrate_thumbnails(
        dry_run=args.dry_run,
        limit=args.limit,
        hours=args.hours
    )


if __name__ == "__main__":
    main()
