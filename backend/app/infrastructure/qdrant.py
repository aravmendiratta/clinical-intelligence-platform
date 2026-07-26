# backend/app/infrastructure/qdrant.py

"""Utility to obtain a Qdrant client.

The client reads connection details from environment variables:
- QDRANT_HOST (default: "qdrant")
- QDRANT_PORT (default: 6333)
- QDRANT_API_KEY (optional, for cloud deployments)
"""

import os
from qdrant_client import QdrantClient


def get_qdrant_client() -> QdrantClient:
    host = os.getenv("QDRANT_HOST", "qdrant")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    api_key = os.getenv("QDRANT_API_KEY")
    if api_key:
        return QdrantClient(host=host, port=port, api_key=api_key)
    return QdrantClient(host=host, port=port)
