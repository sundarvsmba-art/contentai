import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from ..core.database import Content, Trend, get_db
from ..routes.auth_routes import require_admin
from ..services.content_service import create_content_from_trend
from ..services.queue_service import enqueue_generation
from ..services.trend_service import VALID_CATEGORIES, get_trend, list_trends, save_trends
from ..services.trends.trend_fetcher import fetch_all_trends
from ..services.trends.viral_scorer import calculate_viral_score

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["trends"])


@router.get("/trends")
def get_trends(
    category: str = None,
    page: int = 1,
    page_size: int = 30,
    db: Session = Depends(get_db),
):
    if page_size > 100:
        page_size = 100
    offset = (page - 1) * page_size
    trends = list_trends(db, category=category, limit=page_size, offset=offset)
    return JSONResponse([
        {
            "id": t.id,
            "category": t.category,
            "topic": t.topic,
            "source": t.source,
            "viral_score": t.viral_score,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in trends
    ])


@router.post("/fetch-trends")
def fetch_trends(
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    raw = fetch_all_trends()
    for item in raw:
        item["viral_score"] = calculate_viral_score(item["topic"], item["category"])
    saved = save_trends(db, raw)
    return JSONResponse({"fetched": len(raw), "saved": saved})


@router.post("/generate-from-trend/{trend_id}")
def generate_from_trend(
    trend_id: int,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    trend = get_trend(db, trend_id)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    content = create_content_from_trend(db, trend)
    enqueue_generation(content.id, content.topic, content.category or 'general')
    return JSONResponse({"id": content.id, "status": content.status, "topic": content.topic})


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_content = db.query(Content).count()
    recent_trends = (
        db.query(Trend)
        .filter(Trend.created_at >= datetime.utcnow() - timedelta(hours=24))
        .count()
    )
    ready_content = db.query(Content).filter(Content.status == "ready").count()
    avg_raw = (
        db.query(sqlfunc.avg(Content.viral_score))
        .filter(Content.viral_score.isnot(None))
        .scalar()
    )
    avg_score = round(float(avg_raw), 1) if avg_raw else 0.0
    return JSONResponse({
        "total_content": total_content,
        "recent_trends": recent_trends,
        "ready_content": ready_content,
        "avg_viral_score": avg_score,
    })


@router.get("/categories")
def get_categories():
    labels = {
        'tamil_politics': 'Tamil Politics',
        'global_news': 'Global News',
        'ai_tech': 'AI / Tech',
        'celebrity': 'Celebrity',
        'emotional': 'Emotional',
    }
    return JSONResponse([
        {"value": k, "label": v} for k, v in labels.items() if k in VALID_CATEGORIES
    ])
