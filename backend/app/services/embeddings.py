# backend/app/services/embeddings.py
"""Embedding service using sentence-transformers (local, no API key)."""

import logging
from typing import List

from ..core.config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except ImportError:
            logger.warning("sentence-transformers not installed — using dummy embeddings")
            _model = "dummy"
    return _model


def embed_text(text: str) -> List[float]:
    """Generate a vector embedding for the given text.

    Uses the local sentence-transformers model specified in settings.
    Falls back to a zero vector if the library is not installed.
    """
    model = _get_model()
    if model == "dummy":
        return [0.0] * settings.EMBEDDING_DIM

    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch embedding for multiple texts."""
    model = _get_model()
    if model == "dummy":
        return [[0.0] * settings.EMBEDDING_DIM for _ in texts]

    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [e.tolist() for e in embeddings]
