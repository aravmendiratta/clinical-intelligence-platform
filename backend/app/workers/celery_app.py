# backend/app/workers/celery_app.py

"""Celery application configuration for the Clinical Intelligence Platform.

The worker connects to Redis (as defined by the ``REDIS_URL`` environment variable)
and discovers tasks in the ``backend.app.workers`` package.
"""

import os
from celery import Celery

# Build the broker URL from env vars; default to redis://redis:6379/0 as in docker-compose
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "clinical_intel",
    broker=redis_url,
    backend=redis_url,
    include=["backend.app.workers.tasks"],
)
# alias for backward compatibility
app = celery_app

# Optional: configure task serialization (JSON is safe and default)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
