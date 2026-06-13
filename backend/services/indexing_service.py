class IndexingService:
    async def index_document(self, document: dict) -> bool:
        return True

    async def rebuild_index(self) -> bool:
        return True
