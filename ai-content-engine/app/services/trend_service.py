import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from ..core.database import Trend

logger = logging.getLogger(__name__)

VALID_CATEGORIES = frozenset({
    'tamil_politics', 'global_news', 'ai_tech', 'celebrity', 'emotional',
})


def save_trends(db: Session, trends: List[dict]) -> int:
    """Insert trends, skipping duplicates seen within the last 24 hours. Returns count saved."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    count = 0
    for t in trends:
        topic = (t.get('topic') or '').strip()
        category = t.get('category', 'global_news')
        source = t.get('source', 'rss')
        viral_score = int(t.get('viral_score', 0))

        if not topic or len(topic) > 500:
            continue
        if category not in VALID_CATEGORIES:
            category = 'global_news'

        duplicate = (
            db.query(Trend)
            .filter(Trend.topic == topic, Trend.category == category, Trend.created_at >= cutoff)
            .first()
        )
        if duplicate:
            continue

        db.add(Trend(topic=topic, category=category, source=source, viral_score=viral_score))
        count += 1

    if count:
        db.commit()
    logger.info("save_trends: %s new records inserted", count)
    return count


def list_trends(
    db: Session,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Trend]:
    q = db.query(Trend).order_by(Trend.viral_score.desc(), Trend.created_at.desc())
    if category and category in VALID_CATEGORIES:
        q = q.filter(Trend.category == category)
    return q.limit(limit).offset(offset).all()


def get_trend(db: Session, trend_id: int) -> Optional[Trend]:
    return db.query(Trend).filter(Trend.id == trend_id).first()
