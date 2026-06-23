import uuid
from datetime import datetime


class DocumentService:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.documents = {}

    async def upload_document(self, filename: str, content: bytes) -> dict:
        doc_id = str(uuid.uuid4())
        self.documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "size": len(content),
            "status": "uploaded",
        }
        return self.documents[doc_id]

    async def list_documents(self) -> list:
        return list(self.documents.values())

    async def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            doc = self.documents[doc_id]
            await self.vector_store.delete_by_source(doc["filename"])
            del self.documents[doc_id]
            return True
        return False

    async def get_document(self, doc_id: str) -> dict:
        return self.documents.get(doc_id)
