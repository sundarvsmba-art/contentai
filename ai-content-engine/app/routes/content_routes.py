from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.content_service import generate_async, list_contents, update_content_status
from ..schemas.content import ContentCreate, ContentOut
from ..core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post('/generate')
def generate(payload: ContentCreate, db: Session = Depends(get_db)):
    if not payload.topic or len(payload.topic) > settings.MAX_TOPIC_LENGTH:
        raise HTTPException(status_code=400, detail="Invalid topic")
    content_id, status = generate_async(db, payload.topic)
    return JSONResponse({"id": content_id, "status": status})


@router.get('/contents')
def contents(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    rows = list_contents(db, limit=page_size, offset=offset)
    return JSONResponse([{
        "id": r.id,
        "topic": r.topic,
        "script": r.script,
        "status": r.status,
        "error_message": r.error_message,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    } for r in rows])


@router.patch('/content/{content_id}/status')
def patch_status(content_id: int, status: str, db: Session = Depends(get_db)):
    if status not in ('draft', 'ready', 'posted', 'failed'):
        raise HTTPException(status_code=400, detail='Invalid status')
    updated = update_content_status(db, content_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail='Content not found')
    return JSONResponse({"id": updated.id, "status": updated.status})


@router.get('/health')
def health():
    return JSONResponse({"status": "ok"})
