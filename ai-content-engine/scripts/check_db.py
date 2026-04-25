"""Check DB connectivity using app settings.

Usage:
    python scripts/check_db.py

This script will attempt a SQLAlchemy connection to the configured database
using `app.core.config.settings` and print the result.
"""
import sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings


def make_url():
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


def main():
    url = make_url()
    print(f"Testing DB connection to: {url}")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("DB connection successful; test query returned:", result.scalar())
    except SQLAlchemyError as e:
        print("DB connection failed:")
        traceback.print_exc()
        sys.exit(2)
    except Exception:
        print("Unexpected error testing DB connection:")
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
