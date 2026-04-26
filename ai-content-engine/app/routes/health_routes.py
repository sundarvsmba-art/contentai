import logging

import redis as redis_lib
import requests
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from ..core.config import settings
from ..core.database import engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    db_ok = _check_db()
    redis_ok = _check_redis()
    ollama_ok = _check_ollama()
    overall = "ok" if db_ok and redis_ok else "degraded"
    return JSONResponse({
        "status": overall,
        "db": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
        "ollama": "online" if ollama_ok else "offline",
        "gemini": "configured" if settings.GEMINI_API_KEY else "not_configured",
    })


@router.get("/health/db")
def health_db():
    ok = _check_db()
    return JSONResponse({"status": "connected" if ok else "disconnected"})


@router.get("/health/redis")
def health_redis():
    ok = _check_redis()
    return JSONResponse({"status": "connected" if ok else "disconnected"})


@router.get("/health/ollama")
def health_ollama():
    ok = _check_ollama()
    return JSONResponse({
        "status": "online" if ok else "offline",
        "url": settings.OLLAMA_URL,
        "model": settings.OLLAMA_MODEL,
    })


# ------------------------------------------------------------------
# Internal checkers
# ------------------------------------------------------------------

def _check_db() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    try:
        r = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=3)
        r.ping()
        return True
    except Exception:
        return False


def _check_ollama() -> bool:
    try:
        resp = requests.get(f"{settings.OLLAMA_URL.rstrip('/')}/", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False
