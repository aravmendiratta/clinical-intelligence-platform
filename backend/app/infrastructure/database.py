# backend/app/infrastructure/database.py
"""SQLAlchemy database session management.

This module creates the engine, session factory, and a dependency
function that can be injected into FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://medintel:medintel@postgres/medintel")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """FastAPI dependency that provides a DB session and ensures it
    is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
