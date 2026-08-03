# backend/app/routers/chat.py
"""RAG Chat endpoints with SSE streaming."""

import json
from uuid import UUID

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from ..infrastructure.database import get_db
from ..domain.models.chat import Conversation, Message
from ..domain.models.user import User
from ..core.deps import get_current_user
from ..services.chat import chat_stream
from ..services.audit import log_event

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────
class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ChatMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    citations: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ── Endpoints ────────────────────────────────────────────────
@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    body: CreateConversationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = Conversation(title=body.title, user_id=user.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    log_event(db, user_id=user.id, action="create_conversation",
              resource_type="conversation", resource_id=str(conv.id))
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        created_at=conv.created_at.isoformat() if conv.created_at else None,
        updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
    )


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
        .all()
    )
    return [
        ConversationResponse(
            id=str(c.id),
            title=c.title,
            created_at=c.created_at.isoformat() if c.created_at else None,
            updated_at=c.updated_at.isoformat() if c.updated_at else None,
        )
        for c in convs
    ]


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(
        Conversation.id == UUID(conversation_id),
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            citations=m.citations,
            created_at=m.created_at.isoformat() if m.created_at else None,
        )
        for m in messages
    ]


@router.post("/{conversation_id}/message")
async def send_message(
    conversation_id: str,
    body: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message and receive a streaming SSE response."""
    conv = db.query(Conversation).filter(
        Conversation.id == UUID(conversation_id),
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv_id_obj = conv.id
    user_id_obj = user.id

    log_event(db, user_id=user_id_obj, action="chat_query",
              resource_type="conversation", resource_id=conversation_id,
              detail=body.content[:200])

    async def event_generator():
        from ..infrastructure.database import SessionLocal
        stream_db = SessionLocal()
        try:
            async for token in chat_stream(
                user_message=body.content,
                conversation_id=conv_id_obj,
                user_id=user_id_obj,
                db=stream_db,
            ):
                yield {"data": json.dumps({"token": token})}
            yield {"data": json.dumps({"done": True})}
        finally:
            stream_db.close()

    return EventSourceResponse(event_generator())
