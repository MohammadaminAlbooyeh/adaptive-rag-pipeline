class CacheService:
    async def get(self, key: str):
        return None

    async def set(self, key: str, value, ttl: int = 3600):
        pass

    async def invalidate(self, key: str):
        pass
