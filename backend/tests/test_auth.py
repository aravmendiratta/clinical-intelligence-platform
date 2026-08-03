# backend/tests/test_auth.py
"""Tests for authentication endpoints."""


def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "newuser@hospital.com",
        "password": "securepass123",
        "full_name": "Dr. New User",
        "role": "doctor",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@hospital.com"
    assert data["full_name"] == "Dr. New User"
    assert data["role"] == "doctor"


def test_register_duplicate_email(client):
    # Register first
    client.post("/auth/register", json={
        "email": "dup@hospital.com",
        "password": "pass123",
        "full_name": "User",
    })
    # Try duplicate
    response = client.post("/auth/register", json={
        "email": "dup@hospital.com",
        "password": "pass456",
        "full_name": "User 2",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client):
    # Register
    client.post("/auth/register", json={
        "email": "login@hospital.com",
        "password": "pass123",
        "full_name": "Login User",
    })
    # Login
    response = client.post("/auth/login", json={
        "email": "login@hospital.com",
        "password": "pass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "wrong@hospital.com",
        "password": "correct",
        "full_name": "User",
    })
    response = client.post("/auth/login", json={
        "email": "wrong@hospital.com",
        "password": "incorrect",
    })
    assert response.status_code == 401


def test_me_authenticated(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@hospital.com"


def test_me_defaults_to_demo(client):
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "demo@medintel.ai"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
