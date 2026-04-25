from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .core.database import create_tables
from .core.limiter import limiter
from .core.logging import setup_logging
from .middleware.request_logging import RequestLoggingMiddleware
from .routes.auth_routes import router as auth_router
from .routes.content_routes import router as content_router
from .routes.trend_routes import router as trend_router

setup_logging()
 
app = FastAPI(title="AI Trend Content Platform", version="2.0.0")

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Static files (optional)
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates — path relative to this file's directory (app/templates/)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(trend_router)
app.include_router(content_router)

# gunicorn entrypoint
application = app
