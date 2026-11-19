from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.cache import get_redis
from app.auth.security import (
    decode_jwt_token,
)
from app.models.User import User
from app.repositories.User import UserRepository


bearer_scheme = HTTPBearer(auto_error=False)


def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """Extrae el token del header Authorization: Bearer <token>.

    Args:
        request: Objeto Request de FastAPI
        credentials: Credenciales del scheme HTTPBearer

    Returns:
        El token string

    Raises:
        HTTPException: 401 si el header ausente o formato inválido
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente",
        )
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_token_from_request),
    db_session: AsyncSession = Depends(get_session),
) -> User:
    """Dependency que valida el token JWT y retorna el usuario autenticado.

    Pasos:
    1. Decodificar JWT con SECRET_KEY y ALGORITHM=HS256
    2. Extraer jti y consultar Redis blacklist
    3. Si jti está blacklistado → 401 "Token invalidado"
    4. Consultar BD por usuario con email del payload (sub)
    5. Si usuario es None → 401 "Usuario no encontrado"
    6. Si usuario.is_active es False → 403 "Usuario inactivo"
    7. Retorna objeto User con id, email, role

    Args:
        token: Token JWT extraído del header Authorization
        db_session: Sesión de base de datos inyectada

    Returns:
        Objeto User autenticado

    Raises:
        HTTPException: 401 token ausente/inválido/expirado/invalidado,
                       403 usuario inactivo
    """
    # Paso 1: Decodificar JWT
    try:
        payload = decode_jwt_token(token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    jti = payload.get("jti")
    sub = payload.get("sub")

    if jti is None or sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin claims requeridos (jti o sub)",
        )

    # Paso 2: Consultar Redis blacklist
    try:
        redis_client = get_redis()
        jti_blacklisted = await redis_client.get(f"auth:blacklist:{jti}")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de sesión no disponible. Intente nuevamente más tarde.",
        )

    if jti_blacklisted is not None:
        # Paso 3: Si jti está en blacklist → token invalidado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalidado. Ha sido revocado previamente.",
        )

    # Paso 4: Consultar BD por usuario usando el email del claim sub
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_email(sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    # Paso 5: Verificar que usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user