# backend/app/infrastructure/database.py
"""SQLAlchemy database session management with intelligent fallback.

Attempts to connect to Enterprise PostgreSQL; if offline (e.g. during local developer evaluation
or portfolio showcasing without Docker), gracefully falls back to a self-contained SQLite relational store.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import OperationalError

from ..core.config import settings

logger = logging.getLogger(__name__)

# Intelligent Database Connection Engine
try:
    if "sqlite" in settings.DATABASE_URL.lower():
        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        # Check connection availability
        with engine.connect() as conn:
            pass
    logger.info("Successfully connected to primary configured database.")
except Exception as e:
    logger.warning(f"Primary PostgreSQL database unreachable ({e}). Falling back to local SQLite store for zero-friction demo mode.")
    sqlite_url = "sqlite:///./medintel_demo.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a DB session and ensures it
    is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
