from celery import Celery
from ..core.config import settings
from ..services.ai.gemini_provider import GeminiProvider
from ..core.database import SessionLocal, engine
from ..core.database import Content
from ..services.content_service import generate_sync_and_save
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

celery = Celery('worker')
celery.conf.broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL


@celery.task(name='app.workers.celery_worker.generate_task')
def generate_task(content_id: int, topic: str):
    db: Session = SessionLocal()
    try:
        # Mark as in-progress
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            logger.error('Content id not found: %s', content_id)
            return
        content.status = 'ready'
        db.add(content)
        db.commit()

        # Use content_service to generate and save synchronously
        generate_sync_and_save(db, content_id, topic)
    finally:
        db.close()
