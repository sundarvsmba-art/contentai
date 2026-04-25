from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
from ..core.config import settings
import time
import logging

logger = logging.getLogger(__name__)


def _build_database_url():
    return (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


DATABASE_URL = _build_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Trend(Base):
    __tablename__ = 'trends'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(64), nullable=False, index=True)
    topic = Column(Text, nullable=False)
    source = Column(String(64), nullable=False)
    viral_score = Column(Integer, nullable=False, default=0)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    contents = relationship("Content", back_populates="trend")


class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(Text, nullable=False)
    script = Column(Text, nullable=False, default='')
    status = Column(String(32), nullable=False, default='draft', index=True)
    error_message = Column(Text, nullable=True)
    # Viral content fields (populated for trend-generated content)
    hook = Column(Text, nullable=True)
    reel_title = Column(String(256), nullable=True)
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)      # JSON-encoded list
    category = Column(String(64), nullable=True, index=True)
    viral_score = Column(Integer, nullable=True)
    trend_id = Column(Integer, ForeignKey('trends.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    trend = relationship("Trend", back_populates="contents")


def create_tables(max_retries: int = 5, retry_delay: float = 2.0):
    attempt = 0
    while True:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ensured")
            return
        except Exception:
            attempt += 1
            if attempt >= max_retries:
                logger.exception("Failed to create tables after %s attempts", attempt)
                raise
            logger.warning("create_tables attempt %s failed, retry in %ss", attempt, retry_delay)
            time.sleep(retry_delay)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
