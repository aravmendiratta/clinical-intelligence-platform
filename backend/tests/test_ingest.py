# backend/tests/test_ingest.py
"""Tests for document ingestion endpoints."""

import io


def test_upload_document(client):
    """Document upload should work seamlessly without login barriers in demo mode."""
    file_content = b"This is a test clinical document with patient history."
    response = client.post(
        "/ingest/",
        files={"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["filename"] == "test_doc.txt"


def test_get_task_status(client):
    file_content = b"Test content for status check."
    upload_res = client.post(
        "/ingest/",
        files={"file": ("status_test.txt", io.BytesIO(file_content), "text/plain")},
    )
    task_id = upload_res.json()["task_id"]

    response = client.get(f"/ingest/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] in ["queued", "processing", "completed", "failed"]


def test_list_documents(client):
    response = client.get("/ingest/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_task_not_found(client):
    response = client.get("/ingest/nonexistent-id")
    assert response.status_code == 404
