# backend/app/domain/models/audit.py
"""Immutable audit log for compliance and traceability."""

import uuid
from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID

from ...infrastructure.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # nullable for system events
    action = Column(String, nullable=False)  # e.g. "login", "upload_document", "chat_query"
    resource_type = Column(String, nullable=True)  # e.g. "document", "conversation"
    resource_id = Column(String, nullable=True)
    detail = Column(Text, nullable=True)  # JSON or plain-text detail
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
