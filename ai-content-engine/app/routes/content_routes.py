import logging

import redis
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import engine, get_db
from ..core.limiter import limiter
from ..routes.auth_routes import require_admin
from ..schemas.content import ContentCreate
from ..services.content_service import (
    VALID_STATUSES,
    generate_async,
    list_contents,
    update_content_status,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate")
@limiter.limit(settings.RATE_LIMIT_GENERATE)
def generate(request: Request, payload: ContentCreate, db: Session = Depends(get_db)):
    topic = (payload.topic or "").strip()
    if not topic or len(topic) > settings.MAX_TOPIC_LENGTH:
        raise HTTPException(status_code=400, detail="Topic must be 1–200 characters")
    category = (getattr(payload, 'category', None) or 'general').strip()
    content_id, status = generate_async(db, topic, category)
    return JSONResponse({"id": content_id, "status": status})


@router.get("/contents")
def contents(
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    category: str = None,
    db: Session = Depends(get_db),
):
    if page_size > 100:
        page_size = 100
    offset = (page - 1) * page_size
    rows = list_contents(db, limit=page_size, offset=offset, status=status, category=category)
    return JSONResponse([
        {
            "id": r.id,
            "topic": r.topic,
            "script": r.script,
            "hook": r.hook,
            "reel_title": r.reel_title,
            "caption": r.caption,
            "hashtags": r.hashtags,
            "category": r.category,
            "viral_score": r.viral_score,
            "status": r.status,
            "error_message": r.error_message,
            "trend_id": r.trend_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in rows
    ])


@router.post("/status/{content_id}")
def patch_status(
    content_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    status = (payload.get("status") or "").strip()
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {sorted(VALID_STATUSES)}")
    updated = update_content_status(db, content_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Content not found")
    return JSONResponse({"id": updated.id, "status": updated.status})


@router.get("/health")
def health():
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    redis_status = "connected"
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception:
        redis_status = "disconnected"

    overall = "ok" if db_status == "connected" and redis_status == "connected" else "degraded"
    return JSONResponse({"status": overall, "db": db_status, "redis": redis_status})
