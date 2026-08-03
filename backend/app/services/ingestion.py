# backend/app/services/ingestion.py
"""Document ingestion service — saves uploaded files, creates DB records, dispatches Celery jobs."""

import uuid
import os
from fastapi import UploadFile
from sqlalchemy.orm import Session
from ..domain.models.document import Document, IngestionTask


def enqueue_ingestion(file: UploadFile, db: Session, user_id=None) -> str:
    """Persist uploaded file metadata, create IngestionTask, and dispatch a Celery job.
    Returns the task UUID.
    """
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads"))
    os.makedirs(uploads_dir, exist_ok=True)

    # Add UUID prefix to avoid filename collisions
    safe_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(uploads_dir, safe_filename)
    with open(file_path, "wb") as out_f:
        out_f.write(file.file.read())

    # Create Document record
    doc = Document(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        path=file_path,
        uploaded_by=user_id,
    )
    db.add(doc)
    db.flush()  # get doc.id

    task_id = str(uuid.uuid4())
    ingestion_task = IngestionTask(
        id=task_id,
        document_id=doc.id,
        status="queued",
    )
    db.add(ingestion_task)
    db.commit()

    # Dispatch Celery job with inline fallback for local showcasing
    try:
        from ..workers.celery_app import celery_app
        celery_app.send_task("tasks.process_document", args=[task_id])
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Celery queue unreachable ({e}). Running document processing inline.")
        try:
            from ..workers.tasks import process_document
            process_document(task_id)
        except Exception as inline_err:
            logging.getLogger(__name__).error(f"Inline processing failed: {inline_err}")
    return task_id
