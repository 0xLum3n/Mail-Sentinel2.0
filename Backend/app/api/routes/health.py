from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.db.postgres import get_engine
from app.db.redis import get_redis_client

router = APIRouter(tags=["Health"])


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness() -> dict[str, Any]:
    checks: dict[str, str] = {}

    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
        checks["postgresql"] = "ok"
    except Exception:
        checks["postgresql"] = "error"

    try:
        await get_redis_client().ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    healthy = all(value == "ok" for value in checks.values())
    return {"status": "ok" if healthy else "degraded", "checks": checks}