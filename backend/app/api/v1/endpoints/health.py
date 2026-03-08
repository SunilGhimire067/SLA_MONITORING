from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_db
from app.db.redis import redis_pool

router = APIRouter()


@router.get("")
async def health_check():
    return {"status": "healthy", "service": "ITSM Platform"}


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    health = {"status": "healthy", "components": {}}

    # Check MySQL
    try:
        await db.execute(text("SELECT 1"))
        health["components"]["mysql"] = {"status": "healthy"}
    except Exception as e:
        health["components"]["mysql"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"

    # Check Redis
    try:
        await redis_pool.ping()
        health["components"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"

    return health
