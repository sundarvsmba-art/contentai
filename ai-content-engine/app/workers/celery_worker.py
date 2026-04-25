import logging

from celery import Celery
from celery.schedules import crontab

from ..core.config import settings
from ..core.database import Content, SessionLocal
from ..services.content_service import generate_sync_and_save

logger = logging.getLogger(__name__)

celery = Celery("worker")
celery.conf.broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL
celery.conf.timezone = "UTC"
celery.conf.beat_schedule = {
    "fetch-trends-every-2-hours": {
        "task": "app.workers.celery_worker.fetch_trends_task",
        "schedule": crontab(minute=0, hour="*/2"),
    },
}


@celery.task(name="app.workers.celery_worker.generate_task")
def generate_task(content_id: int, topic: str, category: str = "general"):
    db = SessionLocal()
    try:
        row = db.query(Content).filter(Content.id == content_id).first()
        if not row:
            logger.error("generate_task: Content id=%s not found", content_id)
            return

        logger.info("generate_task: start id=%s topic=%s category=%s", content_id, topic, category)
        row.status = "processing"
        db.add(row)
        db.commit()

        result = generate_sync_and_save(db, content_id, topic, category)
        if result:
            logger.info("generate_task: done id=%s status=%s", content_id, result.status)
        else:
            logger.error("generate_task: failed id=%s", content_id)
    except Exception:
        logger.exception("generate_task: unexpected error id=%s", content_id)
    finally:
        db.close()


@celery.task(name="app.workers.celery_worker.fetch_trends_task")
def fetch_trends_task():
    from ..services.trend_service import save_trends
    from ..services.trends.trend_fetcher import fetch_all_trends
    from ..services.trends.viral_scorer import calculate_viral_score

    db = SessionLocal()
    try:
        logger.info("fetch_trends_task: starting scheduled fetch")
        raw = fetch_all_trends()
        for item in raw:
            item["viral_score"] = calculate_viral_score(item["topic"], item["category"])
        saved = save_trends(db, raw)
        logger.info("fetch_trends_task: saved %s new trends from %s fetched", saved, len(raw))
    except Exception:
        logger.exception("fetch_trends_task: failed")
    finally:
        db.close()
