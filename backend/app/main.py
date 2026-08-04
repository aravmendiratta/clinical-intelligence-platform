# backend/app/main.py

"""FastAPI application entry point.

Registers all routers, configures CORS, and sets up application lifecycle.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .infrastructure.database import engine, Base

# Import all models so they are registered with SQLAlchemy
from .domain.models import User, Document, IngestionTask, DocumentChunk, Conversation, Message, AuditLog  # noqa: F401

from .routers.auth import router as auth_router
from .routers.ingest import router as ingest_router
from .routers.search import router as search_router
from .routers.chat import router as chat_router
from .routers.patients import router as patients_router
from .routers.audit import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    import logging
    # Create tables on startup (use Alembic in production)
    Base.metadata.create_all(bind=engine)
    
    def _run_seeding_in_background():
        try:
            from .services.seeder import seed_demo_clinical_data
            from .infrastructure.database import SessionLocal
            db = SessionLocal()
            seed_demo_clinical_data(db)
            db.close()
        except Exception as e:
            logging.getLogger(__name__).warning(f"Demo clinical data seeding error or offline: {e}")

    # Launch background thread so Uvicorn opens TCP ports immediately without timing out on cloud deployments
    asyncio.get_event_loop().run_in_executor(None, _run_seeding_in_background)
    yield


app = FastAPI(
    title="MedIntel — Clinical Intelligence Platform",
    description="AI-powered clinical document analysis with RAG-based chat.",
    version="0.2.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(ingest_router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(patients_router, prefix="/patients", tags=["Dashboard"])
app.include_router(audit_router, prefix="/audit", tags=["Audit"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": app.version}
