# backend/app/routers/search.py
"""Semantic search endpoints using the vector store."""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel

from ..services.retrieval import retrieve_relevant_chunks
from ..domain.models.user import User
from ..core.deps import get_current_user

router = APIRouter()


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    section_title: Optional[str] = None
    content: str
    score: float


@router.get("/", response_model=List[SearchResult])
async def search(
    query: str = Query(..., description="Search query string"),
    limit: int = Query(5, ge=1, le=20),
    user: User = Depends(get_current_user),
):
    """Perform a semantic search across all ingested document chunks."""
    chunks = retrieve_relevant_chunks(query=query, limit=limit)
    return [
        SearchResult(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            filename=c.filename,
            section_title=c.section_title,
            content=c.content,
            score=round(c.score, 4),
        )
        for c in chunks
    ]
