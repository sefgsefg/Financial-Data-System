from celery import Celery

# 初始化 Celery，使用 Redis 作為 Broker 與 Backend
celery_app = Celery(
    "fin_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=['app.workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Taipei',
    enable_utc=True,
    # 預設任務超時設定，防止 Worker 卡死
    task_time_limit=120,
    task_soft_time_limit=100,
)