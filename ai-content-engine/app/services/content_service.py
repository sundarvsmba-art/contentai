import json
import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from ..core.database import Content, Trend
from .queue_service import enqueue_generation
from .ai.provider_router import provider_router

logger = logging.getLogger(__name__)

VALID_STATUSES = frozenset({'draft', 'processing', 'ready', 'posted', 'failed'})


def create_content(db: Session, topic: str, category: str = 'general') -> Content:
    row = Content(topic=topic, script='', status='draft', category=category)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_content_from_trend(db: Session, trend: Trend) -> Content:
    row = Content(
        topic=trend.topic,
        script='',
        status='draft',
        category=trend.category,
        trend_id=trend.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def generate_async(db: Session, topic: str, category: str = 'general') -> Tuple[int, str]:
    content = create_content(db, topic, category)
    enqueue_generation(content.id, content.topic, content.category or 'general')
    return content.id, content.status


def list_contents(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    category: Optional[str] = None,
):
    q = db.query(Content).order_by(Content.created_at.desc())
    if status and status in VALID_STATUSES:
        q = q.filter(Content.status == status)
    if category:
        q = q.filter(Content.category == category)
    return q.limit(limit).offset(offset).all()


def update_content_status(
    db: Session,
    content_id: int,
    status: str,
    error_message: Optional[str] = None,
) -> Optional[Content]:
    row = db.query(Content).filter(Content.id == content_id).first()
    if not row:
        return None
    row.status = status
    if error_message is not None:
        row.error_message = error_message
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def generate_sync_and_save(
    db: Session,
    content_id: int,
    topic: str,
    category: str = 'general',
) -> Optional[Content]:
    try:
        use_viral = category and category != 'general'
        if use_viral:
            result = provider_router.generate_viral_content(topic, category)
            script = result.get('script', '')
            hook = result.get('hook')
            reel_title = result.get('reel_title')
            caption = result.get('caption')
            hashtags_raw = result.get('hashtags', [])
            hashtags = json.dumps(hashtags_raw) if isinstance(hashtags_raw, list) else hashtags_raw
            viral_score = result.get('viral_score')
        else:
            script = provider_router.generate_content(topic)
            hook = reel_title = caption = hashtags = viral_score = None

        row = db.query(Content).filter(Content.id == content_id).first()
        if not row:
            logger.error("Content id=%s not found during save", content_id)
            return None

        row.script = script or ''
        row.hook = hook
        row.reel_title = reel_title
        row.caption = caption
        row.hashtags = hashtags
        row.viral_score = viral_score
        row.status = 'ready'
        row.error_message = None
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    except Exception:
        logger.exception("generate_sync_and_save failed for id=%s", content_id)
        row = db.query(Content).filter(Content.id == content_id).first()
        if row:
            row.status = 'failed'
            row.error_message = 'AI generation failed. Check logs.'
            db.add(row)
            db.commit()
        return None
