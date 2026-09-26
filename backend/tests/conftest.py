import os

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///./test.db",
)

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-for-testing-only",
)

os.environ.setdefault(
    "YOUTUBE_API_KEY",
    "test-youtube-key",
)

os.environ.setdefault(
    "GEMINI_API_KEY",
    "test-gemini-key",
)

os.environ.setdefault(
    "FRONTEND_URL",
    "http://localhost:5173",
)

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client