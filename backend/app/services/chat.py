# backend/app/services/chat.py
"""RAG chat service — retrieval-augmented generation with citation injection."""

import json
import logging
from typing import AsyncGenerator, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..core.config import settings
from ..domain.models.chat import Conversation, Message
from ..services.retrieval import retrieve_relevant_chunks, RetrievedChunk

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are MedIntel, an AI-powered clinical intelligence assistant.
You help clinicians search, summarise, analyse, and reason across clinical documents.

IMPORTANT RULES:
1. Base your answers ONLY on the provided context chunks. Do NOT hallucinate medical information.
2. When referencing information, cite the source using [Source: filename, Section: section] format.
3. If the context does not contain enough information, say so clearly.
4. Never replace or substitute medical judgment — always recommend consulting the treating physician.
5. Be concise, accurate, and professional.

CONTEXT CHUNKS:
{context}
"""


def _build_context(chunks: List[RetrievedChunk]) -> str:
    """Format retrieved chunks into the context block for the system prompt."""
    if not chunks:
        return "(No relevant documents found)"
    parts = []
    for i, c in enumerate(chunks, 1):
        section = f", Section: {c.section_title}" if c.section_title else ""
        parts.append(
            f"[{i}] Source: {c.filename}{section} (score: {c.score:.2f})\n{c.content}"
        )
    return "\n\n---\n\n".join(parts)


def _build_citations(chunks: List[RetrievedChunk]) -> str:
    """Serialize citation metadata as JSON."""
    cites = [
        {
            "index": i,
            "filename": c.filename,
            "section": c.section_title,
            "document_id": c.document_id,
            "chunk_id": c.chunk_id,
            "score": round(c.score, 3),
        }
        for i, c in enumerate(chunks, 1)
    ]
    return json.dumps(cites)


async def chat_stream(
    user_message: str,
    conversation_id: UUID,
    user_id: UUID,
    db: Session,
) -> AsyncGenerator[str, None]:
    """Stream a RAG-augmented response.

    1. Retrieve relevant chunks.
    2. Build system prompt with context.
    3. Stream LLM completion token-by-token.
    4. Persist messages to DB.
    """
    # ── Step 1: Retrieve ─────────────────────────────────────
    chunks = retrieve_relevant_chunks(user_message, limit=5, db=db)
    context = _build_context(chunks)
    citations_json = _build_citations(chunks)

    # ── Persist user message ─────────────────────────────────
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
    )
    db.add(user_msg)
    db.commit()

    # ── Step 2: Build messages ───────────────────────────────
    system_prompt = _SYSTEM_PROMPT.format(context=context)

    # Load conversation history (last 10 messages for context window)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )
    history.reverse()

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    # ── Step 3: Stream from LLM ──────────────────────────────
    full_response = ""

    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                stream=True,
                temperature=0.3,
                max_tokens=2048,
            )
            async for event in stream:
                delta = event.choices[0].delta if event.choices else None
                if delta and delta.content:
                    full_response += delta.content
                    yield delta.content
        except Exception as exc:
            logger.error("OpenAI streaming failed: %s", exc)
            fallback = f"I found {len(chunks)} relevant document(s) but encountered an error generating the response. Please check your OpenAI API key."
            full_response = fallback
            yield fallback
    else:
        # No LLM key — return a formatted summary of retrieved chunks
        fallback = _build_fallback_response(chunks)
        full_response = fallback
        yield fallback

    # ── Step 4: Persist assistant message ────────────────────
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=full_response,
        citations=citations_json,
    )
    db.add(assistant_msg)
    db.commit()


def _build_fallback_response(chunks: List[RetrievedChunk]) -> str:
    """When no LLM is configured, synthesize an extractive summary from top retrieved chunks."""
    if not chunks:
        return "⚠️ No clinical documents containing matching semantic vectors or medical keywords were found in the workspace. Please try refining your clinical terms or uploading additional patient records in the Upload tab."

    top = chunks[0]
    section_info = f" | Section: {top.section_title}" if top.section_title else ""

    lines = [
        "### 🧬 MedIntel RAG Clinical Synthesis (Extractive Engine)",
        "Based on real-time retrieval from your clinical repository, here are the primary verifiable findings for your inquiry:\n",
        f"#### **Primary Clinical Excerpt (`{top.filename}`{section_info})**:",
        f"> *\"{top.content.strip()}\"*\n",
        "---\n",
        "#### **📚 Verifiable Supporting Citations & Evidence Matrix:**"
    ]

    for i, c in enumerate(chunks, 1):
        sec = f" — Section: `{c.section_title}`" if c.section_title else ""
        lines.append(f"- **[{i}]** `{c.filename}`{sec} *(Relevance Score: {c.score:.0%})*")

    lines.append("\n*Note: Response synthesized via MedIntel's high-precision Extractive RAG engine. To activate generative conversational completions, configure `OPENAI_API_KEY` in your `.env` workspace.*")
    return "\n".join(lines)
