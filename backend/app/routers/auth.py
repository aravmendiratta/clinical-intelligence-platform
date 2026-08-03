# backend/app/routers/auth.py
"""Authentication endpoints: register, login, and profile."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..domain.models.user import User, UserRole
from ..core.security import hash_password, verify_password, create_access_token
from ..core.deps import get_current_user
from ..services.audit import log_event

router = APIRouter()


# ── Request / Response schemas ───────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    password: str
    role: UserRole = UserRole.DOCTOR


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


# ── Endpoints ────────────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_event(db, user_id=user.id, action="register", resource_type="user", resource_id=str(user.id))

    return UserResponse(
        id=str(user.id), email=user.email, full_name=user.full_name,
        role=user.role.value, is_active=user.is_active, is_superuser=user.is_superuser,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id, user.role.value)
    log_event(db, user_id=user.id, action="login", resource_type="user", resource_id=str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id), email=user.email, full_name=user.full_name,
        role=user.role.value, is_active=user.is_active, is_superuser=user.is_superuser,
    )
