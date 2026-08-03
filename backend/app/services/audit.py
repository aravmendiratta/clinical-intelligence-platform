# backend/app/services/audit.py
"""Audit logging service – writes immutable records to the audit_logs table."""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from ..domain.models.audit import AuditLog


def log_event(
    db: Session,
    *,
    user_id: Optional[UUID] = None,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Create an immutable audit log entry."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
