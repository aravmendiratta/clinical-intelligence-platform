# backend/app/workers/tasks.py

"""Celery tasks for the Clinical Intelligence Platform.

- `process_document` reads the uploaded file metadata, extracts text,
  chunks it, generates vector embeddings, stores them in Qdrant,
  and updates the ingestion task status.
"""

import os
import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from ..infrastructure.database import SessionLocal
from ..infrastructure.qdrant import get_qdrant_client
from ..domain.models.document import Document, IngestionTask, DocumentChunk
from ..services.embeddings import embed_text, embed_texts
from ..services.chunking import chunk_text
from ..core.config import settings

logger = logging.getLogger(__name__)


def _update_task_status(session: Session, task_id: str, status: str, error: Optional[str] = None) -> None:
    """Utility to update the `IngestionTask` row."""
    task = session.query(IngestionTask).filter(IngestionTask.id == task_id).first()
    if not task:
        logger.error("IngestionTask %s not found", task_id)
        return
    task.status = status
    task.error_message = error
    session.commit()


def _extract_text_from_file(filepath: str, filename: str) -> str:
    """Extract plain text from a file on disk.

    Supports PDF, DOCX, images (OCR), and plain text fallback.
    """
    suffix = os.path.splitext(filename)[1].lower()

    with open(filepath, "rb") as f:
        raw = f.read()

    if suffix == ".pdf":
        try:
            from pdfminer.high_level import extract_text as pdf_extract_text
            import tempfile
            tmp = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.pdf")
            with open(tmp, "wb") as tf:
                tf.write(raw)
            try:
                return pdf_extract_text(tmp) or ""
            finally:
                os.remove(tmp)
        except Exception as exc:
            logger.warning("PDF extraction failed for %s: %s", filename, exc)
            return ""

    if suffix in {".docx", ".doc"}:
        try:
            import docx
            import tempfile
            tmp = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.docx")
            with open(tmp, "wb") as tf:
                tf.write(raw)
            try:
                doc = docx.Document(tmp)
                return "\n".join(p.text for p in doc.paragraphs)
            finally:
                os.remove(tmp)
        except Exception as exc:
            logger.warning("DOCX extraction failed for %s: %s", filename, exc)
            return ""

    if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        try:
            from PIL import Image
            import pytesseract
            from io import BytesIO
            img = Image.open(BytesIO(raw))
            return pytesseract.image_to_string(img)
        except Exception as exc:
            logger.warning("OCR extraction failed for %s: %s", filename, exc)
            return ""

    # Fallback: try UTF-8 decode
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def process_document(task_id: str) -> None:
    """Celery entry point.

    Steps:
    1. Retrieve the `IngestionTask` and associated `Document`.
    2. Extract raw text from the stored file.
    3. Chunk the text into medical sections.
    4. Generate embeddings for each chunk.
    5. Upsert the vectors into Qdrant.
    6. Mark the task as ``completed`` (or ``failed`` on exception).
    """
    session = SessionLocal()
    try:
        # 1. Load task & document
        task = session.query(IngestionTask).filter(IngestionTask.id == task_id).first()
        if not task:
            raise RuntimeError(f"IngestionTask {task_id} not found")
        doc = session.query(Document).filter(Document.id == task.document_id).first()
        if not doc:
            raise RuntimeError(f"Document id {task.document_id} not found")

        _update_task_status(session, task_id, "processing")

        # 2. Extract text
        if not doc.path or not os.path.isfile(doc.path):
            raise RuntimeError(f"File at {doc.path} does not exist")

        raw_text = _extract_text_from_file(doc.path, doc.filename)
        if not raw_text.strip():
            logger.warning("No text extracted from %s", doc.filename)
            _update_task_status(session, task_id, "completed", "No text could be extracted")
            return

        # 3. Chunk the text
        text_chunks = chunk_text(raw_text)
        if not text_chunks:
            text_chunks = [(raw_text, None)]

        logger.info("Document %s → %d chunks", doc.filename, len(text_chunks))

        # 4. Generate embeddings
        chunk_texts = [content for content, _ in text_chunks]
        embeddings = embed_texts(chunk_texts)

        # 5. Upsert into Qdrant
        qdrant = get_qdrant_client()
        collection_name = settings.QDRANT_COLLECTION

        # Ensure collection exists
        existing = [c.name for c in qdrant.get_collections().collections]
        if collection_name not in existing:
            from qdrant_client.models import VectorParams, Distance
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )

        # Create DB chunk records and upsert vectors
        points = []
        for i, ((content, section_title), vector) in enumerate(zip(text_chunks, embeddings)):
            chunk_record = DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=content,
                section_title=section_title,
            )
            session.add(chunk_record)
            session.flush()  # get chunk_record.id

            from qdrant_client.models import PointStruct
            points.append(
                PointStruct(
                    id=chunk_record.id,
                    vector=vector,
                    payload={
                        "chunk_id": chunk_record.id,
                        "document_id": doc.id,
                        "filename": doc.filename,
                        "section_title": section_title,
                    },
                )
            )

        if points:
            qdrant.upsert(collection_name=collection_name, points=points)

        session.commit()

        # 6. Mark completed
        _update_task_status(session, task_id, "completed")
        logger.info("Successfully processed document %s (%d chunks)", doc.filename, len(points))

    except Exception as exc:
        logger.exception("Error processing ingestion task %s", task_id)
        _update_task_status(session, task_id, "failed", str(exc))
    finally:
        session.close()
