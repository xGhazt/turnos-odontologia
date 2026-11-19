import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_valid_configuration(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    monkeypatch.setenv("SECRET_KEY", "test-only-secret-key-for-jwt-tests-32-bytes")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    settings = Settings(_env_file=None)

    assert settings.database_url.startswith("postgresql+asyncpg")
    assert settings.cors_origins == ["http://localhost:5173", "http://localhost:3000"]
    assert settings.secret_key == "test-only-secret-key-for-jwt-tests-32-bytes"
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_missing_database_url_raises(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "database_url" in str(exc_info.value).lower()


def test_missing_secret_key_raises(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "secret_key" in str(exc_info.value).lower()


def test_invalid_port_type_raises(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("APP_PORT", "not-a-number")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "app_port" in str(exc_info.value).lower()


def test_invalid_access_token_expire_minutes_raises(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("SECRET_KEY", "test-only-secret-key-for-jwt-tests-32-bytes")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "0")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "access_token_expire_minutes" in str(exc_info.value).lower()


def test_negative_access_token_expire_minutes_raises(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("SECRET_KEY", "test-only-secret-key-for-jwt-tests-32-bytes")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "-5")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "access_token_expire_minutes" in str(exc_info.value).lower()
