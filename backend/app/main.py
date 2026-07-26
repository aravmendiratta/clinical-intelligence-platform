# backend/app/main.py

"""FastAPI application entry point.

- Includes the authentication router (if any) and the ingestion router.
- Registers the search router once it is created.
- Uses the `get_db` dependency from `infrastructure.database`.
"""

from fastapi import FastAPI

from .routers.ingest import router as ingest_router
from .routers.search import router as search_router

app = FastAPI(title="Clinical Intelligence Platform", version="0.1.0")

# Include routers
app.include_router(ingest_router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search_router, prefix="/search", tags=["Search"])
