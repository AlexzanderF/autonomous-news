import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', '6379'))
redis_db = int(os.getenv('REDIS_DB', '0'))
redis_password = os.getenv('REDIS_PASSWORD')

# Build Redis URL for Celery broker and backend
if redis_password:
    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
else:
    redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

# Initialize Celery app
celery_app = Celery(
    'news_workers',
    broker=redis_url,
    backend=redis_url,
    include=[
        'news_generation_workers.tasks.headline_picker',
        'news_generation_workers.tasks.article_generation',
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'pick-headlines-every-4-hours': {
        'task': 'news_generation_workers.tasks.headline_picker.run_headline_picker_cycle',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at minute 0
    },
}