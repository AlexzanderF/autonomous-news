"""
Database connection and session management.

This module provides a centralized database configuration for the entire application,
including FastAPI, Celery workers, and Alembic migrations.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables
load_dotenv()

# ============================================================================
# Database Configuration
# ============================================================================

# Construct database URL from environment variables
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'autonomous_news')

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max overflow connections
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# Session Management Functions
# ============================================================================

def get_db():
    """
    Database session dependency for FastAPI endpoints (AUTOMATIC cleanup).
    
    This is a generator function that yields a session. When used with FastAPI's
    Depends(), it automatically closes the session after the request completes.
    
    Key difference from get_database_session():
    - Uses 'yield' (generator) instead of 'return'
    - FastAPI handles the lifecycle automatically
    - No need to manually close the session
    - The 'finally' block always executes after the endpoint handler
    
    Usage in FastAPI:
        from fastapi import Depends
        from sqlalchemy.orm import Session
        
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
            # Session automatically closed by FastAPI ✅
    
    DO NOT use in Celery workers or scripts - use get_database_session() instead.
    """
    db = SessionLocal()
    try:
        yield db  # FastAPI will resume here after the endpoint completes
    finally:
        db.close()  # Always executes, even if endpoint raises an exception


def get_database_session() -> Session:
    """
    Create and return a new database session (MANUAL cleanup required).
    
    This is a regular function that returns a session. The caller is responsible
    for closing the session when done.
    
    Key difference from get_db():
    - Uses 'return' (regular function) instead of 'yield'
    - Caller must manually close the session
    - Suitable for Celery workers, scripts, and background tasks
    - Not compatible with FastAPI's Depends()
    
    Usage in Celery workers or scripts:
        db = get_database_session()
        try:
            # Do database operations
            article = db.query(Article).first()
            article.status = 'published'
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()  # You MUST close it manually ⚠️
    
    DO NOT use in FastAPI endpoints - use get_db() with Depends() instead.
    """
    return SessionLocal()

