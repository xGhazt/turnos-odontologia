from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.health import check_database, check_redis

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness(
    database_ok: bool = Depends(check_database),
    redis_ok: bool = Depends(check_redis),
) -> JSONResponse:
    dependencies = {
        "database": "ok" if database_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
    }
    if database_ok and redis_ok:
        return JSONResponse(status_code=200, content={"status": "ok", "dependencies": dependencies})
    return JSONResponse(status_code=503, content={"status": "degraded", "dependencies": dependencies})
