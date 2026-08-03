# backend/tests/test_chat.py
"""Tests for RAG chat endpoints."""


def test_create_conversation(client):
    """Creating a chat conversation should succeed out-of-the-box in demo mode."""
    response = client.post("/chat/", json={"title": "Patient Review"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Patient Review"
    assert "id" in data


def test_list_conversations(client):
    client.post("/chat/", json={"title": "List Test"})
    response = client.get("/chat/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_messages_empty(client):
    res = client.post("/chat/", json={"title": "Empty Chat"})
    conv_id = res.json()["id"]

    response = client.get(f"/chat/{conv_id}/messages")
    assert response.status_code == 200
    assert response.json() == []


def test_conversation_not_found(client):
    response = client.get("/chat/00000000-0000-0000-0000-000000000000/messages")
    assert response.status_code == 404
