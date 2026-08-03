# backend/tests/conftest.py
"""Test fixtures for the MedIntel backend test suite."""

import os
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite and mock settings for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["QDRANT_HOST"] = "localhost"
os.environ["QDRANT_PORT"] = "6333"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database import Base, engine, get_db

# Mock external network connections (Celery and Qdrant) to keep tests fast and offline
from app.workers import celery_app
celery_app.send_task = MagicMock(return_value=MagicMock(id="mock-task-id-for-testing"))

from app.infrastructure import qdrant
mock_qdrant_client = MagicMock()
mock_qdrant_client.search.return_value = []
qdrant.get_qdrant_client = MagicMock(return_value=mock_qdrant_client)

# Create test engine with SQLite
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before tests and drop them after."""
    from app.domain.models import User, Document, IngestionTask, DocumentChunk, Conversation, Message, AuditLog  # noqa
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except PermissionError:
            pass


@pytest.fixture
def client():
    """Return a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Return a test database session."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers(client):
    """Register a test user (if not already existing) and return auth headers."""
    # Attempt login first in case user was registered by a previous test in session
    res = client.post("/auth/login", json={
        "email": "test@hospital.com",
        "password": "testpassword123",
    })
    if res.status_code != 200:
        client.post("/auth/register", json={
            "email": "test@hospital.com",
            "password": "testpassword123",
            "full_name": "Dr. Test User",
            "role": "doctor",
        })
        res = client.post("/auth/login", json={
            "email": "test@hospital.com",
            "password": "testpassword123",
        })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    """Register an admin user (if not already existing) and return auth headers."""
    from app.domain.models.user import User, UserRole
    from app.core.security import hash_password
    import uuid

    db = TestSessionLocal()
    admin = db.query(User).filter(User.email == "admin@hospital.com").first()
    if not admin:
        admin = User(
            id=uuid.uuid4(),
            email="admin@hospital.com",
            full_name="Admin User",
            hashed_password=hash_password("adminpass123"),
            role=UserRole.ADMIN,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
    db.close()

    res = client.post("/auth/login", json={
        "email": "admin@hospital.com",
        "password": "adminpass123",
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
