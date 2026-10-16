from sqlalchemy import text

from app.core.cache import get_redis
from app.core.db import get_engine


async def check_database() -> bool:
    """Devuelve True si PostgreSQL responde a una consulta trivial."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def check_redis() -> bool:
    """Devuelve True si Redis responde al PING."""
    try:
        client = get_redis()
        await client.ping()
        return True
    except Exception:
        return False
