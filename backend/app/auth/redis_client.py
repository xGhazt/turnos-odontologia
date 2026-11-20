import redis
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool

from app.core.settings import get_settings

settings = get_settings()


_redis_client = None


def get_redis_client() -> redis.Redis:
    """Obtiene o crea una instancia de cliente Redis.

    Returns:
        Cliente Redis configurado con la URL del settings.

    Raises:
        HTTPException: Si la configuración de Redis es inválida.
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail="Servicio de sesión no disponible. Intente nuevamente más tarde.",
            )
    return _redis_client


async def async_redis_set(key: str, value: str, ttl: int = None) -> bool:
    """Establece un valor en Redis de forma asíncrona usando ThreadPoolExecutor.

    Args:
        key: Llave de Redis
        value: Valor a almacenar
        ttl: Tiempo en segundos hasta expiración. Si es None, sin TTL.

    Returns:
        True si la operación fue exitosa.

    Raises:
        HTTPException: Si Redis no está disponible.
    """
    client = get_redis_client()
    return await run_in_threadpool(_redis_set_sync, client, key, value, ttl)


async def async_redis_get(key: str) -> str | None:
    """Obtiene un valor de Redis de forma asíncrona usando ThreadPoolExecutor.

    Args:
        key: Llave de Redis

    Returns:
        Valor almacenado o None si la clave no existe.

    Raises:
        HTTPException: Si Redis no está disponible.
    """
    client = get_redis_client()
    return await run_in_threadpool(_redis_get_sync, client, key)


async def async_redis_del(key: str) -> int:
    """Elimina una llave de Redis de forma asíncrona usando ThreadPoolExecutor.

    Args:
        key: Llave de Redis a eliminar

    Returns:
        Número de llaves eliminadas (0 o 1).

    Raises:
        HTTPException: Si Redis no está disponible.
    """
    client = get_redis_client()
    return await run_in_threadpool(_redis_del_sync, client, key)


def _redis_set_sync(client: redis.Redis, key: str, value: str, ttl: int | None) -> bool:
    """Versión síncrona para setear en Redis."""
    try:
        if ttl is not None:
            client.setex(key, ttl, value)
        else:
            client.set(key, value)
        return True
    except Exception:
        return False


def _redis_get_sync(client: redis.Redis, key: str) -> str | None:
    """Versión síncrona para obtener de Redis."""
    try:
        return client.get(key)
    except Exception:
        return None


def _redis_del_sync(client: redis.Redis, key: str) -> int:
    """Versión síncrona para eliminar de Redis."""
    try:
        return client.delete(key)
    except Exception:
        return 0