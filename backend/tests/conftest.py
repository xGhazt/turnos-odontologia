import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

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


@pytest.fixture
def db_session():
    """Session síncrona aislada en SQLite en memoria para tests de modelos."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
