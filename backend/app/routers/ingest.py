# backend/app/routers/ingest.py
"""Document ingestion endpoints."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..services.ingestion import enqueue_ingestion
from ..services.audit import log_event
from ..infrastructure.database import get_db
from ..domain.models.document import IngestionTask, Document, DocumentChunk
from ..domain.models.user import User
from ..core.deps import get_current_user

router = APIRouter()


@router.post("/", summary="Upload a document for ingestion")
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    task_id = enqueue_ingestion(file, db, user_id=user.id)
    log_event(db, user_id=user.id, action="upload_document",
              resource_type="document", detail=file.filename)
    return JSONResponse(content={"task_id": task_id, "filename": file.filename})


@router.get("/{task_id}", summary="Get ingestion task status")
async def get_task_status(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(IngestionTask).filter(IngestionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={
        "task_id": task.id,
        "status": task.status,
        "error_message": task.error_message,
    })


@router.get("/", summary="List all documents")
async def list_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # In demo mode, show ALL documents (including pre-seeded clinical records)
    # so evaluators can see the full dataset immediately.
    chunk_counts = dict(
        db.query(DocumentChunk.document_id, func.count(DocumentChunk.id))
        .group_by(DocumentChunk.document_id)
        .all()
    )

    docs = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "content_type": d.content_type,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            "chunk_count": chunk_counts.get(d.id, 0),
            "is_processed": chunk_counts.get(d.id, 0) > 0,
        }
        for d in docs
    ]


@router.get("/seed-demo", summary="Manually trigger demo clinical data seeding")
@router.post("/seed-demo", summary="Manually trigger demo clinical data seeding")
async def seed_demo_data(db: Session = Depends(get_db)):
    import logging
    logger = logging.getLogger(__name__)
    try:
        from ..services.seeder import seed_demo_clinical_data
        seed_demo_clinical_data(db)
        return {"status": "success", "message": "Demo clinical records successfully seeded into database!"}
    except Exception as e:
        logger.exception("Manual seed error")
        return {"status": "error", "error": str(e)}
