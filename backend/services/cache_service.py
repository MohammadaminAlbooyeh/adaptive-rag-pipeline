import time
from typing import Optional, Any


class CacheService:
    def __init__(self):
        self._cache: dict = {}
        self._ttls: dict = {}

    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if key in self._ttls and time.time() > self._ttls[key]:
                del self._cache[key]
                del self._ttls[key]
                return None
            return self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        self._cache[key] = value
        self._ttls[key] = time.time() + ttl

    async def invalidate(self, key: str):
        self._cache.pop(key, None)
        self._ttls.pop(key, None)

    async def clear(self):
        self._cache.clear()
        self._ttls.clear()
