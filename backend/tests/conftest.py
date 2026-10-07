import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

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


from app.dependencies import get_current_user
from app.main import app


@pytest.fixture
def client():
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_client():
    async def override_get_current_user():
        return SimpleNamespace(
            id=1,
            username="testuser",
            email="test@example.com",
        )

    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()