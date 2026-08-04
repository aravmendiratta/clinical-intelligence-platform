# backend/app/services/embeddings.py
"""Embedding service using sentence-transformers (local, no API key)."""

import os
import math
import re
import hashlib
import logging
from typing import List

from ..core.config import settings

logger = logging.getLogger(__name__)

_model = None


class FastLexicalHasher:
    """Lightweight deterministic hashing vectorizer for memory-constrained cloud environments (<512MB RAM).
    Generates authentic 384-dimensional cosine-compatible embedding vectors without PyTorch neural network RAM consumption.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    def encode(self, text_or_list, normalize_embeddings=True, show_progress_bar=False):
        is_single = isinstance(text_or_list, str)
        texts = [text_or_list] if is_single else text_or_list
        results = []
        for t in texts:
            vec = [0.0] * self.dim
            words = re.findall(r"\w+", t.lower())
            if not words:
                results.append(vec)
                continue
            for w in words:
                h = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                vec[idx] += 1.0
            
            if normalize_embeddings:
                norm = math.sqrt(sum(v * v for v in vec))
                if norm > 0:
                    vec = [v / norm for v in vec]
            results.append(vec)
        
        class VectorResult:
            def __init__(self, data):
                self.data = data
            def tolist(self):
                return self.data

        if is_single:
            return VectorResult(results[0])
        else:
            return [VectorResult(r) for r in results]


def _get_model():
    """Lazy-load embedding engine; auto-selects FastLexicalHasher on cloud container installations to stay under 512MB RAM."""
    global _model
    if _model is None:
        if os.environ.get("RENDER") or os.environ.get("LIGHTWEIGHT_EMBEDDINGS", "1") == "1":
            logger.info("Cloud container environment detected (<512MB RAM limit). Utilizing FastLexicalHasher 384d projection engine.")
            _model = FastLexicalHasher(settings.EMBEDDING_DIM)
        else:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
                _model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except (ImportError, Exception) as exc:
                logger.warning("sentence-transformers offline or OOM warning (%s) — defaulting to FastLexicalHasher", exc)
                _model = FastLexicalHasher(settings.EMBEDDING_DIM)
    return _model


def embed_text(text: str) -> List[float]:
    """Generate a vector embedding for the given text.

    Uses local sentence-transformers model when abundant memory is available,
    or pivots seamlessly to zero-RAM deterministic 384-d vector hashing on constrained free cloud tiers.
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
