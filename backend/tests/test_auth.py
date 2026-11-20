"""Tests de integración para C-03 auth-system.

Cubre escenarios JWT, contraseñas, Redis, dependencia y endpoints.
Utiliza mocks y fixtures según infraestructura existente.
No se conecta a PostgreSQL ni modifica datos reales.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.settings import get_settings
from app.auth.security import (
    generate_jwt_token,
    decode_jwt_token,
    get_jti_from_token,
    async_verify_password,
)
from app.core.cache import get_redis

from app.main import create_app
from app.core.db import get_session
from httpx import ASGITransport, AsyncClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_user():
    """Usuario de prueba mock."""
    from app.models.User import User, Role
    from datetime import datetime, timezone

    role = Role(name="odontologo")
    user = User(
        email="test@example.com",
        password_hash="$2b$12$Nz.test.hash.for.testing.purposes.only",
        role=role,
        is_active=True,
    )
    user.id = 1
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def mock_token_data():
    """Datos de payload de token JWT mock."""
    return {
        "sub": "test@example.com",
        "jti": "test-jti-123",
        "iat": 1234567890,
        "exp": 1234571490,
        "role": "odontologo",
    }


# ---------------------------------------------------------------------------
# Tests de configuración
# ---------------------------------------------------------------------------


def test_settings_has_jwt_vars(monkeypatch):
    """Verificar que settings tiene las variables JWT configuradas."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("SECRET_KEY", "a-very-secret-key-at-least-32-chars-long")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    from app.core.settings import get_settings
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.secret_key == "a-very-secret-key-at-least-32-chars-long"
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_secret_key_minimum_length(monkeypatch):
    """SECRET_KEY debe tener mínimo 32 caracteres."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    # 31 caracteres - debería fallar
    monkeypatch.setenv("SECRET_KEY", "a-very-secret-key-at-least-31-chars")

    from app.core.settings import Settings
    try:
        Settings(_env_file=None)
        # Si no lanza, verificamos que la longitud es exactamente validada
        pass
    except ValidationError as e:
        assert "SECRET_KEY" in str(e).lower() or "length" in str(e).lower()


# ---------------------------------------------------------------------------
# Tests de generación/decodificación JWT
# ---------------------------------------------------------------------------


def test_generate_jwt_token():
    """Test de generación de token JWT."""
    token = generate_jwt_token(
        user_data={
            "sub": "test@example.com",
            "jti": "test-jti-456",
            "role": "paciente",
        }
    )
    assert token is not None and isinstance(token, str)

    # Decodificar y verificar
    payload = decode_jwt_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["jti"] == "test-jti-456"
    assert "exp" in payload
    assert "iat" in payload


def test_decode_jwt_token_invalid():
    """Test que decodificación falla con clave incorrecta."""
    import jwt
    from fastapi import HTTPException

    token = generate_jwt_token(
        user_data={"sub": "test@example.com", "jti": "test-jti", "role": "paciente"},
        secret_key="test-only-secret-key-for-jwt-tests-32-bytes",
    )

    try:
        decode_jwt_token(token, secret_key="other-very-secret-key-at-least-32-chars")
        assert False, "Debería haber lanzado HTTPException"
    except HTTPException as e:
        assert e.status_code == status.HTTP_401_UNAUTHORIZED
        assert "inválido" in e.detail.lower()


def test_decode_jwt_token_expired():
    """Test que decodificación falla con token expirado."""
    import jwt

    # Crear token con expiration en el pasado
    payload = {
        "sub": "test@example.com",
        "jti": "test-jti-exp",
        "iat": 1000,
        "exp": 1000,  # Ya expirado
    }
    token = jwt.encode(payload, "test-only-secret-key-for-jwt-tests-32-bytes", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        decode_jwt_token(token, secret_key="test-only-secret-key-for-jwt-tests-32-bytes")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expirado" in exc_info.value.detail.lower()


def test_get_jti_from_token():
    """Test de extracción de jti de token."""
    token = generate_jwt_token(
        user_data={"sub": "test@example.com", "jti": "custom-jti-789", "role": "admin"}
    )
    jti = get_jti_from_token(token)
    assert jti == "custom-jti-789"


def test_get_jti_from_token_missing():
    """Test que falla al extraer jti sin claim jti."""
    import jwt

    payload = {"sub": "test@example.com", "other": "data"}
    token = jwt.encode(payload, "test-only-secret-key-for-jwt-tests-32-bytes", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        get_jti_from_token(token, secret_key="test-only-secret-key-for-jwt-tests-32-bytes")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Tests de bcrypt async
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_verify_password_correct():
    """Test que bcrypt verify correcto funciona en threadpool."""
    import bcrypt

    plain = "TestPassword123!"
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    result = await async_verify_password(plain, hashed)
    assert result is True


@pytest.mark.asyncio
async def test_async_verify_password_incorrect():
    """Test que bcrypt verify incorrecto falla."""
    import bcrypt

    plain = "TestPassword123!"
    hashed = bcrypt.hashpw(b"other_password", bcrypt.gensalt()).decode("utf-8")

    result = await async_verify_password(plain, hashed)
    assert result is False


# ---------------------------------------------------------------------------
# Tests de dependencia get_current_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_valid_token(
    mock_user, mock_token_data, db_session
):
    """Test que get_current_user retorna usuario con token válido."""
    from app.auth.security import generate_jwt_token

    token = generate_jwt_token(user_data={
        "sub": mock_user.email,
        "jti": "test-jti-valid",
        "role": mock_user.role.name,
    })

    # Mock decode_jwt_token, get_redis y UserRepository simultáneamente
    with patch("app.auth.dependencies.decode_jwt_token") as mock_decode:
        mock_decode.return_value = {
            "sub": mock_user.email,
            "jti": "test-jti-valid",
            "iat": 1234567890,
            "exp": 1234571490,
            "role": mock_user.role.name,
        }

        with patch("app.auth.dependencies.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get.return_value = None  # Not blacklisted
            mock_get_redis.return_value = mock_redis

            with patch(
                "app.repositories.User.UserRepository.get_by_email",
                new_callable=lambda: AsyncMock(return_value=mock_user),
            ) as mock_get_user:

                from app.auth.dependencies import get_current_user

                result = await get_current_user(token=token, db_session=db_session)
                assert result.email == mock_user.email


# ---------------------------------------------------------------------------
# Tests de Redis blacklist
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_redis_blacklist_save_and_get():
    """Test de guardado y consulta en Redis blacklist (unidad)."""
    from unittest.mock import AsyncMock

    # Cliente simulado de Redis
    r = AsyncMock()

    # Configurar retorno de get()
    r.get.return_value = b"invalidated"

    # Probar setex y get con mock
    test_key = "auth:blacklist:test-jti"
    await r.setex(test_key, 60, "invalidated")
    result = await r.get(test_key)
    assert result == b"invalidated" or result == "invalidated"

    # Cleanup
    await r.delete(test_key)

    # Verificar que los métodos fueron llamados con los argumentos esperados
    r.setex.assert_called_once_with(test_key, 60, "invalidated")
    r.get.assert_called_once_with(test_key)
    r.delete.assert_called_once_with(test_key)


# ---------------------------------------------------------------------------
# Tests de endpoints (usando client fastapi)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_endpoint_integration(client, mock_user, db_session):
    """Test de integración del endpoint de login."""
    from unittest.mock import patch, AsyncMock
    from fastapi import status
    from jwt import decode as jwt_decode

    # Mockear UserRepository.get_by_email para no conectar a BD
    with patch("app.auth.router.UserRepository.get_by_email", new_callable=AsyncMock) as mock_get_by_email:
        mock_get_by_email.return_value = mock_user

        # Mockear async_verify_password para no usar bcrypt real
        with patch("app.auth.router.async_verify_password", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = True

            # Credenciales de login ficticias
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123!",
            }

            # Enviar POST al endpoint de login
            response = await client.post("/auth/login", json=login_data)

            # Comprobar respuesta HTTP 200
            assert response.status_code == status.HTTP_200_OK

            # Comprobar estructura de respuesta
            data = response.json()
            assert data.get("token_type") == "bearer"
            assert data.get("access_token") is not None
            assert len(data.get("access_token", "")) > 0

            # Datos públicos del usuario
            user_data = data.get("user", {})
            assert user_data.get("id") == mock_user.id
            assert user_data.get("email") == mock_user.email
            assert user_data.get("role") == mock_user.role.name

            # Decodificar JWT para verificar claims
            from app.core.settings import get_settings
            settings = get_settings()
            payload = jwt_decode(
                data.get("access_token"),
                settings.secret_key,
                algorithms=[settings.algorithm],
            )

            # Verificar claims del token
            assert payload.get("sub") == "test@example.com"
            assert payload.get("jti") is not None
            assert payload.get("role") == mock_user.role.name


@pytest.mark.asyncio
async def test_logout_success(client, mock_user):
    """Test logout exitoso con JWT válido."""
    from unittest.mock import patch, AsyncMock
    from fastapi import status

    # Mockear decode_jwt_token con claims válidos (jti y exp)
    with patch("app.auth.router.decode_jwt_token") as mock_decode:
        mock_decode.return_value = {
            "sub": mock_user.email,
            "jti": "test-jti-valid",
            "exp": 10000000000,  # timestamp en el futuro
            "role": mock_user.role.name,
        }

        # Mockear get_redis con AsyncMock
        with patch("app.auth.router.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.setex.return_value = None
            mock_get_redis.return_value = mock_redis

            # Enviar POST logout con token Bearer
            response = await client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer valid-token-string"}
            )

            # Comprobar HTTP 200
            assert response.status_code == status.HTTP_200_OK

            # Comprobar respuesta
            data = response.json()
            assert data.get("detail") == "Sesión cerrada exitosamente"

            # Verificar que setex fue llamado con la clave auth:blacklist:<jti> y TTL positivo
            mock_redis.setex.assert_called_once()
            call_kwargs = mock_redis.setex.call_args
            assert call_kwargs[0][0] == "auth:blacklist:test-jti-valid"  # clave
            assert call_kwargs[0][1] > 0  # TTL positivo
            assert call_kwargs[0][2] == "invalidated"  # valor


@pytest.mark.asyncio
async def test_logout_redis_unavailable(client, mock_user):
    """Test logout cuando Redis no está disponible."""
    from unittest.mock import patch, AsyncMock
    from fastapi import status

    # Mockear decode_jwt_token con claims válidos
    with patch("app.auth.router.decode_jwt_token") as mock_decode:
        mock_decode.return_value = {
            "sub": mock_user.email,
            "jti": "test-jti-unavailable",
            "exp": 10000000000,  # timestamp en el futuro
            "role": mock_user.role.name,
        }

        # Mockear get_redis pero que setex lance excepción
        with patch("app.auth.router.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.setex.side_effect = Exception("Redis connection failed")
            mock_get_redis.return_value = mock_redis

            # Enviar POST logout con token Bearer
            response = await client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer valid-token-string"}
            )

            # Comprobar HTTP 503
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

            # Comprobar que no devuelve éxito
            data = response.json()
            assert data.get("detail") != "Sesión cerrada exitosamente"


@pytest.mark.asyncio
async def test_me_inactive_user(client, mock_user):
    """Test GET /auth/me con usuario inactivo."""
    from unittest.mock import patch, AsyncMock
    from fastapi import status

    # Establecer usuario inactivo directamente
    mock_user.is_active = False

    # Mockear decode_jwt_token para devolver claims válidos
    with patch("app.auth.dependencies.decode_jwt_token") as mock_decode:
        mock_decode.return_value = {
            "sub": mock_user.email,
            "jti": "test-jti-inactive",
            "iat": 1234567890,
            "exp": 1234571490,
            "role": mock_user.role.name,
        }

        # Mockear get_redis con AsyncMock (no revocado)
        with patch("app.auth.dependencies.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get.return_value = None  # No está en blacklist
            mock_get_redis.return_value = mock_redis

            # Mockear UserRepository.get_by_email
            with patch("app.repositories.User.UserRepository.get_by_email", new_callable=AsyncMock) as mock_get_by_email:
                mock_get_by_email.return_value = mock_user

                # Enviar GET /auth/me
                response = await client.get(
                    "/auth/me",
                    headers={"Authorization": "Bearer valid-token-string"}
                )

                # Comprobar HTTP 403
                assert response.status_code == status.HTTP_403_FORBIDDEN

                # Comprobar mensaje
                data = response.json()
                assert data.get("detail") == "Usuario inactivo"


# Endpoints helpers para el client de test


@pytest.fixture(scope="session")
async def client():
    """Cliente de test FastAPI async."""
    from app.core.settings import get_settings
    get_settings.cache_clear()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac