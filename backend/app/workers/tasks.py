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
from ..services.ingestion import extract_text
from ..workers.celery_app import celery_app

logger = logging.getLogger(__name__)
import logging
from typing import List

from sqlalchemy.orm import Session

from ..infrastructure.database import SessionLocal, Document, IngestionTask
from ..infrastructure.qdrant import get_qdrant_client
from ..services.ingestion import extract_text

logger = logging.getLogger(__name__)


def embed_text(text: str) -> List[float]:
    """Generate a text embedding using Google Gemini API.

    The Gemini embedding model is accessed via the `google-generativeai` SDK.
    The API key is read from the `GEMINI_API_KEY` environment variable.
    The function caches the client for the lifetime of the process.
    """
    import os
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")

    # Initialise the client only once per process
    if not hasattr(embed_text, "_client"):
        genai.configure(api_key=api_key)
        embed_text._client = genai.EmbeddingModel("embedding-001")

    response = embed_text._client.embed_content(text)
    return list(response.embedding)


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
        raw_text = extract_text(upload_file)
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
