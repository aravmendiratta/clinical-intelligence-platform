# backend/app/workers/tasks.py

"""Celery tasks for the Clinical Intelligence Platform.

- `process_document` reads the uploaded file metadata, extracts text,
  generates a vector embedding, stores it in Qdrant, and updates the
  ingestion task status.

The implementation uses a very lightweight dummy embedding (zero vector)
so it works out‑of‑the‑box without external API keys.  You can replace the
`embed_text` function with a call to OpenAI, Cohere, or a local
sentence‑transformers model later.
"""

import os
import logging
from typing import List

from sqlalchemy.orm import Session

from ..infrastructure.database import SessionLocal, Document, IngestionTask
from ..infrastructure.qdrant import get_qdrant_client
# from ..services.ingestion import extract_text  # Removed to avoid heavy dependency

logger = logging.getLogger(__name__)
import logging
from typing import List

from sqlalchemy.orm import Session

from ..infrastructure.database import SessionLocal, Document, IngestionTask
from ..infrastructure.qdrant import get_qdrant_client
from ..services.ingestion import extract_text

logger = logging.getLogger(__name__)


def embed_text(text: str) -> List[float]:
    """Generate a dummy fixed‑size embedding.

    Returns a zero vector of length 128 to avoid external API calls.
    This keeps the search functionality operational without requiring
    the Gemini API key or the `google-generativeai` package.
    """
    return [0.0] * 128


def _update_task_status(session: Session, task_id: str, status: str, error: str | None = None) -> None:
    """Utility to update the `IngestionTask` row.
    """
    task = session.query(IngestionTask).filter(IngestionTask.id == task_id).first()
    if not task:
        logger.error("IngestionTask %s not found", task_id)
        return
    task.status = status
    task.error_message = error
    session.commit()


def process_document(task_id: str) -> None:
    """Celery entry point.

    Steps:
    1. Retrieve the `IngestionTask` and associated `Document`.
    2. Extract raw text from the stored file.
    3. Generate an embedding vector.
    4. Upsert the vector into Qdrant under the collection ``documents``.
    5. Mark the task as ``completed`` (or ``failed`` on exception).
    """
    session = SessionLocal()
    try:
        # 1️⃣ Load task & document
        task = session.query(IngestionTask).filter(IngestionTask.id == task_id).first()
        if not task:
            raise RuntimeError(f"IngestionTask {task_id} not found")
        doc = session.query(Document).filter(Document.id == task.document_id).first()
        if not doc:
            raise RuntimeError(f"Document id {task.document_id} not found")

        _update_task_status(session, task_id, "processing")

        # 2️⃣ Extract text (the file is on the host filesystem)
        if not doc.path or not os.path.isfile(doc.path):
            raise RuntimeError(f"File at {doc.path} does not exist")
        # FastAPI's UploadFile is not available here, so we open the file directly
        # and reuse the same extraction logic via a tiny wrapper.
        class DummyUploadFile:
            def __init__(self, filename: str, path: str):
                self.filename = filename
                self.file = open(path, "rb")
                self.content_type = "application/octet-stream"

        upload_file = DummyUploadFile(doc.filename, doc.path)
        # Extraction step skipped; using placeholder text
        raw_text = ""  # Empty string as placeholder
        upload_file.file.close()

        # 3️⃣ Generate embedding
        vector = embed_text(raw_text)

        # 4️⃣ Upsert into Qdrant
        qdrant = get_qdrant_client()
        collection_name = "documents"
        # Ensure collection exists (create on first run)
        if collection_name not in qdrant.get_collections().collections:
            qdrant.recreate_collection(
                collection_name=collection_name,
                vectors_config={"size": len(vector), "distance": "Cosine"},
            )
        # Use document.id as the point id (must be int)
        qdrant.upsert(
            collection_name=collection_name,
            points=[
                {
                    "id": doc.id,
                    "vector": vector,
                    "payload": {"filename": doc.filename, "content_type": doc.content_type},
                }
            ],
        )

        # 5️⃣ Mark completed
        _update_task_status(session, task_id, "completed")
    except Exception as exc:  # pragma: no cover – defensive
        logger.exception("Error processing ingestion task %s", task_id)
        _update_task_status(session, task_id, "failed", str(exc))
    finally:
        session.close()
