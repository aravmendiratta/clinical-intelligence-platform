# backend/tests/test_search.py
"""Tests for search endpoints."""


def test_search_returns_list(client):
    """Search should work directly in demo mode without required auth headers."""
    response = client.get("/search/?query=diabetes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
