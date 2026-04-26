from pydantic import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    GEMINI_API_KEY: Optional[str] = None
    DB_HOST: str = "db"
    DB_NAME: str = "ai_content"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_PORT: int = 5432
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    MAX_TOPIC_LENGTH: int = 200
    APP_PORT: int = 2000

    # Admin auth
    SECRET_KEY: str = "change-me-in-production-32-chars!!"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Ollama (local AI — auto-detected via health check)
    OLLAMA_URL: str = "http://host.docker.internal:11434"
    OLLAMA_MODEL: str = "phi3"

    # Optional News API key (newsapi.org)
    NEWS_API_KEY: Optional[str] = None

    # Rate limiting
    RATE_LIMIT_GENERATE: str = "10/minute"

    class Config:
        env_file = Path(__file__).resolve().parents[2] / '.env'


settings = Settings()
