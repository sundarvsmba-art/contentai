# AI Content Engine

Small FastAPI application that generates short emotional medical stories using Google Gemini (mocked by default).

Prerequisites
- Docker & Docker Compose

Quick start

1. Copy and edit `.env` with your credentials (GEMINI_API_KEY and DB credentials if needed).
2. Start the full stack (backend, db, redis, worker):

```powershell
docker-compose up --build
```

3. Open http://localhost:8000 in your browser.

Notes on background processing
- The generation is handled asynchronously by Celery workers. The `worker` service runs Celery and listens on Redis.
- The backend enqueues jobs to Redis; the worker pulls tasks, calls the configured AI provider, and updates the DB.

Project structure

See `app/` for the FastAPI source. Key files:
- `app/services/ai/*` — AI provider implementations (base_provider.py, gemini_provider.py)
- `app/core/database.py` — SQLAlchemy models and session management
- `app/routes/content_routes.py` — API endpoints
- `app/templates/index.html` — Jinja2 dashboard

Notes & future work
- Replace the placeholder Gemini call with an authenticated client per Google's docs.
- Add tests, retries, logging, and background job processing for long-running generation.
- Add OpenAI provider as an alternate AI backend.
