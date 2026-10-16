import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.core.settings import get_settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def app():
    get_settings.cache_clear()
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
