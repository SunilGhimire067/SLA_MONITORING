import json
import logging
from typing import Any, Callable, Coroutine, Optional

import redis.asyncio as aioredis

from app.db.redis import redis_pool

logger = logging.getLogger(__name__)


class CacheService:
    """
    Thin async wrapper around Redis providing get / set / delete
    and a cache-aside (get_or_set) pattern.
    """

    def __init__(self, redis: Optional[aioredis.Redis] = None):
        self._redis: aioredis.Redis = redis or redis_pool

    # ------------------------------------------------------------------ #
    #  Core operations
    # ------------------------------------------------------------------ #

    async def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from the cache.

        Returns None on cache miss or Redis error.
        """
        try:
            value = await self._redis.get(key)
            return value
        except Exception:
            logger.exception("Cache GET failed for key=%s", key)
            return None

    async def set(self, key: str, value: str, ttl: int = 60) -> None:
        """
        Store a value in the cache with a TTL (in seconds).
        """
        try:
            await self._redis.set(key, value, ex=ttl)
        except Exception:
            logger.exception("Cache SET failed for key=%s", key)

    async def delete(self, key: str) -> None:
        """
        Remove a key from the cache.
        """
        try:
            await self._redis.delete(key)
        except Exception:
            logger.exception("Cache DELETE failed for key=%s", key)

    # ------------------------------------------------------------------ #
    #  Cache-aside pattern
    # ------------------------------------------------------------------ #

    async def get_or_set(
        self,
        key: str,
        callback: Callable[[], Coroutine[Any, Any, str]],
        ttl: int = 60,
    ) -> str:
        """
        Cache-aside helper.

        1. Try to read from cache.
        2. On miss, call the async callback to compute the value.
        3. Store the computed value in cache with the given TTL.
        4. Return the value.

        The callback must return a string (use json.dumps for complex data).
        """
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await callback()
        await self.set(key, value, ttl=ttl)
        return value
