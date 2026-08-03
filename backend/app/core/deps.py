# backend/app/core/deps.py
"""FastAPI dependencies for seamless demo mode and RBAC."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..domain.models.user import User, UserRole
from .security import decode_access_token, hash_password
import uuid

_bearer = HTTPBearer(auto_error=False)


def _get_or_create_demo_user(db: Session) -> User:
    """Retrieve or create the default demo user for seamless recruiter/student evaluation."""
    demo_email = "demo@medintel.ai"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        user = User(
            id=uuid.uuid4(),
            email=demo_email,
            full_name="Dr. Demo (Reviewer)",
            hashed_password=hash_password("demomodedisabled"),
            role=UserRole.ADMIN,
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Return the demo user by default so reviewers/recruiters have zero barriers to exploring functionality."""
    if not credentials or credentials.credentials == "demo-token":
        return _get_or_create_demo_user(db)

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            return _get_or_create_demo_user(db)
    except (JWTError, ValueError):
        return _get_or_create_demo_user(db)

    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if user is None or not user.is_active:
        return _get_or_create_demo_user(db)
    return user


def require_role(*allowed_roles: str):
    """Return a dependency that enforces role-based access.

    In demo mode, the default user is an admin and has access to all roles and endpoints.
    """
    async def _guard(user: User = Depends(get_current_user)):
        if user.role.value not in allowed_roles and not user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _guard
