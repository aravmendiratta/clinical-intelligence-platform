# backend/app/infrastructure/qdrant.py

"""Utility to obtain a Qdrant vector client with offline evaluation fallback.

Attempts to connect to Qdrant vector container server; if unreachable during local showcasing,
pivots seamlessly to Qdrant local disk storage without losing semantic search capabilities.
"""

import os
import logging
from qdrant_client import QdrantClient
from ..core.config import settings

logger = logging.getLogger(__name__)

_local_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    global _local_qdrant_client
    try:
        if settings.QDRANT_API_KEY:
            client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
                timeout=2.0,
            )
        else:
            client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=2.0)
        # Test vector server reachability
        client.get_collections()
        return client
    except Exception as e:
        logger.warning("Qdrant Docker server unreachable. Utilizing embedded local Qdrant vector store for demo showcasing.")
        if _local_qdrant_client is None:
            storage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.qdrant_demo_storage"))
            os.makedirs(storage_path, exist_ok=True)
            _local_qdrant_client = QdrantClient(path=storage_path)
        return _local_qdrant_client
