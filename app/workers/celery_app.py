import os
from celery import Celery

# 優先讀取環境變數 (Docker 環境會提供)，否則退回 localhost (本機開發用)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_BACKEND = os.getenv("REDIS_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "fin_worker",
    broker=REDIS_URL,
    backend=REDIS_BACKEND,
    include=['app.workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Taipei',
    enable_utc=True,
    task_time_limit=120,
    task_soft_time_limit=100,
)