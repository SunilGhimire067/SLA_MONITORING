"""Create all database tables from SQLAlchemy models."""
import asyncio
import logging

from app.db.session import engine
from app.db.base import Base
from app.models import *  # noqa: F401,F403 - Import all models so Base.metadata knows about them

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    logger.info("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
