from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .routes.content_routes import router as content_router
from .core.database import create_tables
from .core.logging import setup_logging
from .middleware.request_logging import RequestLoggingMiddleware

setup_logging()

app = FastAPI(title="AI Content Engine")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get('/', response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


app.add_middleware(RequestLoggingMiddleware)
app.include_router(content_router)

# gunicorn entrypoint
application = app
