from celery import Celery
from ..core.config import settings


def make_celery():
    broker = settings.CELERY_BROKER_URL or settings.REDIS_URL
    backend = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL
    celery = Celery('ai_content_engine', broker=broker, backend=backend)
    return celery


celery_app = make_celery()


def enqueue_generation(content_id: int, topic: str):
    # Import here to avoid circular imports
    celery_app.send_task('app.workers.celery_worker.generate_task', args=[content_id, topic])
