# backend/app/infrastructure/database.py
"""SQLAlchemy database session management.

This module creates the engine, session factory, and a dependency
function that can be injected into FastAPI routes.
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://medintel:medintel@postgres/medintel")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# -------------------------------------------------------------------
# Domain models for Document Ingestion
# -------------------------------------------------------------------
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    # optional path if stored on local FS
    path = Column(String, nullable=True)
    # optional metadata JSON (as text)
    extra_metadata = Column(Text, nullable=True)

class IngestionTask(Base):
    __tablename__ = "ingestion_tasks"
    id = Column(String, primary_key=True, index=True)  # UUID string
    document_id = Column(Integer, nullable=False)
    status = Column(String, default="queued")  # queued, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(Text, nullable=True)

def get_db() -> Session:
    """FastAPI dependency that provides a DB session and ensures it
    is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
