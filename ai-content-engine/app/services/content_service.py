from sqlalchemy.orm import Session
from ..core.database import Content
from typing import Tuple
from .queue_service import enqueue_generation
from .ai.gemini_provider import GeminiProvider
import logging

logger = logging.getLogger(__name__)


def create_content(db: Session, topic: str) -> Content:
    new = Content(topic=topic, script="", status='draft')
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


def generate_async(db: Session, topic: str) -> Tuple[int, str]:
    # Create DB row and enqueue a background job
    content = create_content(db, topic)
    enqueue_generation(content.id, topic)
    return content.id, content.status


def list_contents(db: Session, limit: int = 50, offset: int = 0):
    return db.query(Content).order_by(Content.created_at.desc()).limit(limit).offset(offset).all()


def update_content_status(db: Session, content_id: int, status: str, error_message: str | None = None):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        return None
    content.status = status
    if error_message:
        content.error_message = error_message
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def generate_sync_and_save(db: Session, content_id: int, topic: str):
    """Synchronous generation used by worker: calls GeminiProvider and updates DB."""
    provider = GeminiProvider()
    try:
        script = provider.generate_content(topic)
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            logger.error('Content not found: %s', content_id)
            return None
        content.script = script
        content.status = 'posted'
        db.add(content)
        db.commit()
        db.refresh(content)
        return content
    except Exception as e:
        logger.exception('Error generating content for id %s', content_id)
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.status = 'failed'
            content.error_message = str(e)
            db.add(content)
            db.commit()
        return None
