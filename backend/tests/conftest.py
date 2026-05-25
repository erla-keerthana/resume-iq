"""Shared test fixtures."""

import os
import sys
import pytest

# Ensure backend modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set required env vars before any app imports
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5174")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_resumeiq.db")


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine (shared across all tests in the session)."""
    from database import engine, Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Clean up test DB file
    db_path = "test_resumeiq.db"
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_session(db_engine):
    """Yield a fresh DB session per test, rolled back after each test."""
    from database import SessionLocal
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_engine):
    """FastAPI TestClient with the real app (rate limiting disabled)."""
    from main import app, limiter
    from fastapi.testclient import TestClient

    limiter.enabled = False
    c = TestClient(app)
    yield c
    limiter.enabled = True
