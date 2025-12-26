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

# Headline picker schedule times (comma-separated HH:MM format in UTC)
# Example: "11:00,14:30,21:30" for three runs per day
headline_picker_times = os.getenv('HEADLINE_PICKER_TIMES', '11:00,14:30,21:30')

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
        'news_generation_workers.tasks.thumbnail_picker',
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

# Dynamically build Celery Beat schedule from environment variable
beat_schedule = {}

# Parse the comma-separated times and create schedule entries
for idx, time_str in enumerate(headline_picker_times.split(',')):
    time_str = time_str.strip()
    if not time_str:
        continue
    
    try:
        # Parse HH:MM format
        hour, minute = time_str.split(':')
        hour = int(hour)
        minute = int(minute)
        
        # Validate time values
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            print(f"Warning: Invalid time '{time_str}' - skipping")
            continue
        
        # Create a unique task name
        task_name = f'pick-headlines-{hour:02d}{minute:02d}'
        
        # Add to beat schedule
        beat_schedule[task_name] = {
            'task': 'news_generation_workers.tasks.headline_picker.run_headline_picker_cycle',
            'schedule': crontab(minute=minute, hour=hour),
        }
        
    except (ValueError, AttributeError) as e:
        print(f"Warning: Could not parse time '{time_str}' - skipping. Error: {e}")
        continue

celery_app.conf.beat_schedule = beat_schedule