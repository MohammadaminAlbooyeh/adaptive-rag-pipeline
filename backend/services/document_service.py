class DocumentService:
    async def upload(self, file_path: str, metadata: dict = None) -> dict:
        return {"id": "doc_id", "filename": file_path.split("/")[-1]}

    async def list_documents(self) -> list:
        return []

    async def delete_document(self, doc_id: str) -> bool:
        return True
