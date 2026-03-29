import os
from celery import Celery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leadforge-worker")

# Redis configuration from environment variables
# Format: redis://:password@hostname:port
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery_app = Celery(
    "leadforge",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configuration overrides
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max
    worker_prefetch_multiplier=1, # One task per worker at a time for stability on low RAM
)

# Autodiscover tasks from the app
celery_app.autodiscover_tasks(['app.tasks'])

logger.info(f"🚀 Celery initialized with broker: {REDIS_URL.split('@')[-1] if '@' in REDIS_URL else REDIS_URL}")
