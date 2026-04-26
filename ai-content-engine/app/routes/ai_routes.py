import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..services.ai.provider_router import provider_router

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers")
def get_providers():
    """Return live status of all configured AI providers."""
    return JSONResponse(provider_router.provider_status())
