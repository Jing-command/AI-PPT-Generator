"""
Celery 任务队列配置
"""

from celery import Celery

from app.config import settings

# 创建 Celery 实例
celery_app = Celery(
    "ai_ppt",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.export_tasks",
        "app.tasks.generation_tasks",
    ]
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务执行设置
task_track_started=True,
task_time_limit=3600,  # 1小时超时
task_soft_time_limit=3000,  # 50分钟软超时
    
    # 结果过期时间
    result_expires=86400,  # 1天
    
    # 并发设置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 重试设置
    task_default_retry_delay=60,
task_max_retries=3,
)

# 自动发现任务
celery_app.autodiscover_tasks()
