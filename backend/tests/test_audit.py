# backend/tests/test_audit.py
"""Tests for audit log and dashboard endpoints."""


def test_audit_returns_logs(client):
    """Audit logs should be viewable in demo mode since default demo user has admin permissions."""
    response = client.get("/audit/logs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_audit_filter_by_action(client, admin_headers):
    response = client.get("/audit/logs?action=login", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["action"] == "login"


def test_dashboard_returns_stats(client):
    response = client.get("/patients/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_conversations" in data
