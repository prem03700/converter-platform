from celery import Celery

from app.config import settings

celery_app = Celery(
    "converter_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Conversions can be slow (video/office docs) — avoid the worker
    # being killed mid-job and avoid one slow job starving others.
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_time_limit=900,
)

celery_app.autodiscover_tasks(["app.workers"])
