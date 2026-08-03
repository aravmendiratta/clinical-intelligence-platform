# backend/app/services/dashboard.py
"""Dashboard aggregation queries for the patient/admin dashboard."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..domain.models.document import Document, IngestionTask
from ..domain.models.chat import Conversation, Message
from ..domain.models.user import User


def get_dashboard_stats(db: Session, user_id=None) -> Dict[str, Any]:
    """Aggregate dashboard statistics."""
    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    # Document stats
    doc_query = db.query(Document)
    if user_id:
        doc_query = doc_query.filter(Document.uploaded_by == user_id)

    total_documents = doc_query.count()
    recent_documents = doc_query.filter(Document.uploaded_at >= last_7_days).count()

    # Document type breakdown
    type_breakdown = (
        doc_query
        .with_entities(Document.content_type, func.count(Document.id))
        .group_by(Document.content_type)
        .all()
    )

    # Ingestion task stats
    task_stats = (
        db.query(IngestionTask.status, func.count(IngestionTask.id))
        .group_by(IngestionTask.status)
        .all()
    )

    # Conversation stats
    conv_query = db.query(Conversation)
    if user_id:
        conv_query = conv_query.filter(Conversation.user_id == user_id)

    total_conversations = conv_query.count()
    total_messages = db.query(Message).count()

    # Recent uploads (last 10)
    recent_uploads = (
        doc_query
        .order_by(Document.uploaded_at.desc())
        .limit(10)
        .all()
    )

    # Recent conversations (last 5)
    recent_convs = (
        conv_query
        .order_by(Conversation.updated_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_documents": total_documents,
        "recent_documents_7d": recent_documents,
        "document_types": {ct: count for ct, count in type_breakdown},
        "ingestion_status": {status: count for status, count in task_stats},
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "recent_uploads": [
            {
                "id": d.id,
                "filename": d.filename,
                "content_type": d.content_type,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in recent_uploads
        ],
        "recent_conversations": [
            {
                "id": str(c.id),
                "title": c.title,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in recent_convs
        ],
    }
