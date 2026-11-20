import time
from datetime import datetime, timedelta, timezone

import jwt

from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.core.settings import get_settings

settings = get_settings()


def generate_jwt_token(user_data: dict, secret_key: str = None,
                       algorithm: str = "HS256", expire_minutes: int = None) -> str:
    """Genera un token JWT firmado con los claims especificados.

    Args:
        user_data: Diccionario con los claims del usuario (sub, jti, iat, exp, role, etc.)
        secret_key: Clave secreta para firma (default: config SECRET_KEY)
        algorithm: Algoritmo de firma (default: HS256, obligatorio)
        expire_minutes: Minutos hasta expiración (default: config ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        Token JWT codificado como string

    Raises:
        ValueError: Si el algoritmo no es HS256 o la clave es inválida
    """
    if secret_key is None:
        secret_key = settings.secret_key

    if algorithm != "HS256":
        raise ValueError("Only HS256 algorithm is supported")

    if expire_minutes is None:
        expire_minutes = settings.access_token_expire_minutes

    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    issued_at = datetime.now(timezone.utc)

    payload = {
        "sub": user_data.get("sub"),
        "jti": user_data.get("jti"),
        "iat": issued_at,
        "exp": expire,
        "role": user_data.get("role"),
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def decode_jwt_token(token: str, secret_key: str = None,
                     algorithm: str = "HS256") -> dict:
    """Decodifica y valida un token JWT.

    Args:
        token: Token JWT para decodificar
        secret_key: Clave secreta para validación (default: config SECRET_KEY)
        algorithm: Algoritmo de validación (default: HS256)

    Returns:
        Diccionario con los claims del token

    Raises:
        HTTPException: 401 si el token es inválido, expirado o la clave es incorrecta
    """
    if secret_key is None:
        secret_key = settings.secret_key

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


def get_jti_from_token(token: str, secret_key: str = None,
                       algorithm: str = "HS256") -> str:
    """Extrae el claim 'jti' de un token JWT.

    Args:
        token: Token JWT
        secret_key: Clave secreta (default: config SECRET_KEY)
        algorithm: Algoritmo (default: HS256)

    Returns:
        El valor del claim jti

    Raises:
        HTTPException: Si el token es inválido o no contiene jti
    """
    payload = decode_jwt_token(token, secret_key, algorithm)
    jti = payload.get("jti")
    if jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador jti",
        )
    return jti


async def async_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash usando bcrypt en ThreadPoolExecutor.

    Esta función es async y usa run_in_threadpool para no bloquear el event loop
    de FastAPI, ya que bcrypt es una operación síncrona por naturaleza.

    Args:
        plain_password: Contraseña en claro provista por el usuario
        hashed_password: Hash de bcrypt almacenado en la base de datos

    Returns:
        True si la contraseña coincide, False en caso contrario
    """
    return await run_in_threadpool(_verify_password_sync, plain_password, hashed_password)


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    """Versión síncrona de la verificación de contraseña con bcrypt."""
    import bcrypt
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))