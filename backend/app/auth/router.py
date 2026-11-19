from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.core.db import get_session
from app.core.cache import get_redis
from app.core.settings import get_settings
settings = get_settings()
from app.auth.security import (
    generate_jwt_token,
    decode_jwt_token,
    async_verify_password,
)
from app.auth.dependencies import get_current_user
from app.models.User import User
from app.repositories.User import UserRepository
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=dict)
async def login(
    request: LoginRequest,
    db_session: AsyncSession = Depends(get_session),
):
    """Inicia sesión de usuario y genera JWT.

    Flujo:
    1. Buscar usuario por email usando UserRepository
    2. Rechazar usuario inexistente con 401 (mensaje genérico)
    3. Rechazar usuario inactivo con 403
    4. Verificar contraseña mediante async_verify_password
    5. Generar JWT con JTI único (no se agrega a blacklist en login)
    6. Devolver access_token, token_type y datos públicos del usuario

    Args:
        request: Credenciales de login (email y password)
        db_session: Sesión de base de datos inyectada

    Returns:
        Diccionario con access_token, token_type y datos del usuario

    Raises:
        HTTPException: 401 credenciales inválidas, 403 usuario inactivo
    """
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_email(request.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_UNAUTHORIZED,
            detail="Usuario inactivo",
        )

    password_valid = await async_verify_password(request.password, user.password_hash)

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    jti = uuid.uuid4().hex

    token = generate_jwt_token(
        user_data={
            "sub": user.email,
            "jti": jti,
            "role": user.role.name if user.role else "paciente",
        },
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )

    # IMPORTANTE: En login NO se agrega el JTI a Redis blacklist.
    # La blacklist sólo recibe tokens revocados mediante logout.

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name if user.role else "paciente",
        },
    }


@router.get("/me", response_model=dict)
async def get_me(
    user: User = Depends(get_current_user),
):
    """Obtiene el perfil del usuario autenticado.

    Utiliza get_current_user dependency que valida el token y consulta
    Redis blacklist antes de retornar los datos.

    Returns:
        Diccionario con datos públicos del usuario autenticado

    Raises:
        HTTPException: 401 token inválido/expirado/invalidado,
                       403 usuario inactivo
    """
    role_name = user.role.name if user.role else "paciente"

    return {
        "id": user.id,
        "email": user.email,
        "role": role_name,
    }


@router.post("/logout", response_model=dict)
async def logout(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
):
    """Cierra sesión del usuario invalidando el token en Redis.

    Flujo:
    1. Extraer Bearer Token del header Authorization
    2. Rechazar si ausente con 401
    3. Validar JWT mediante decode_jwt_token
    4. Verificar que existan jti y exp
    5. Calcular TTL restante
    6. Si token expiró o TTL <= 0 → 401
    7. Registrar JTI en Redis con TTL calculado
    8. Si Redis falla → 503 sin informar éxito falso
    9. Si Redis confirma → retorno éxito

    Args:
        request: Objeto Request de FastAPI para extraer headers
        credentials: Credenciales HTTPBearer del header Authorization

    Returns:
        Diccionario con mensaje de éxito

    Raises:
        HTTPException: 401 token ausente/inválido/expirado,
                       503 si Redis no disponible
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente",
        )

    token = credentials.credentials

    # Decodificar JWT para obtener JTI y exp
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
    if jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador jti",
        )

    exp = payload.get("exp")
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin claim de expiración",
        )

    now = int(datetime.now(timezone.utc).timestamp())
    ttl = int(exp) - now

    if ttl <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )

    # Registrar JTI en Redis con TTL calculado
    try:
        redis_client = get_redis()
        await redis_client.setex(f"auth:blacklist:{jti}", ttl, "invalidated")
        return {"detail": "Sesión cerrada exitosamente"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de sesión no disponible. Intente nuevamente más tarde.",
        )