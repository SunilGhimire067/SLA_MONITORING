from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "itsm_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.sla_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.escalation_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    "scan-sla-breaches-every-minute": {
        "task": "app.tasks.sla_tasks.scan_sla_breaches",
        "schedule": 60.0,  # every 60 seconds
    },
    "send-sla-warnings-every-5-minutes": {
        "task": "app.tasks.sla_tasks.send_sla_warnings",
        "schedule": 300.0,  # every 5 minutes
    },
}
