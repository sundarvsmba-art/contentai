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

    class Config:
        env_file = Path(__file__).resolve().parents[2] / '.env'


settings = Settings()
