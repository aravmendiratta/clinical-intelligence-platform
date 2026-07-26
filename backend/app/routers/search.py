from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
import os

from ..workers.tasks import embed_text
from ..infrastructure.qdrant import get_qdrant_client
from ..infrastructure.database import SessionLocal, Document

router = APIRouter()

class SearchResult(BaseModel):
    id: int
    filename: str
    content_type: str
    snippet: Optional[str] = None
    score: float

@router.get("/", response_model=List[SearchResult])
async def search(
    query: str = Query(..., description="Search query string"),
    limit: int = Query(5, ge=1, le=20)
):
    # Generate embedding for the query
    vector = embed_text(query)
    qdrant = get_qdrant_client()
    collection_name = "documents"
    # Perform similarity search
    search_result = qdrant.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=limit,
    )
    # Extract IDs and scores
    ids_scores = [(point.id, point.score) for point in search_result]
    ids = [int(id) for id, _ in ids_scores]
    # Fetch document metadata from DB
    db = SessionLocal()
    docs = db.query(Document).filter(Document.id.in_(ids)).all()
    doc_map = {doc.id: doc for doc in docs}
    results = []
    for doc_id, score in ids_scores:
        doc = doc_map.get(int(doc_id))
        if not doc:
            continue
        # Create a snippet (first 200 chars of file if exists)
        snippet = None
        if doc.path and os.path.isfile(doc.path):
            try:
                with open(doc.path, "r", encoding="utf-8") as f:
                    snippet = f.read(200)
            except Exception:
                snippet = None
        results.append(
            SearchResult(
                id=doc.id,
                filename=doc.filename,
                content_type=doc.content_type,
                snippet=snippet,
                score=score,
            )
        )
    db.close()
    return results
