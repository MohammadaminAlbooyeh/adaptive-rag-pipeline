import io
from backend.document_loaders.pdf_loader import PDFLoader
from backend.document_loaders.txt_loader import TXTLoader
from backend.document_loaders.csv_loader import CSVLoader
from backend.document_loaders.docx_loader import DOCXLoader


class IndexingService:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm
        self.chunk_size = 500
        self.chunk_overlap = 50

    async def index_document(self, doc_id: str, filename: str, content: bytes) -> bool:
        try:
            chunks = self._extract_chunks(filename, content)
            if not chunks:
                return False

            documents = [
                {
                    "content": chunk,
                    "metadata": {
                        "source": filename,
                        "doc_id": doc_id,
                        "chunk_index": i,
                    },
                }
                for i, chunk in enumerate(chunks)
            ]

            await self.vector_store.add_documents(documents)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to index document: {str(e)}")

    def _extract_chunks(self, filename: str, content: bytes) -> list:
        try:
            if filename.endswith(".pdf"):
                loader = PDFLoader()
                text = loader.load(io.BytesIO(content))
            elif filename.endswith(".txt"):
                loader = TXTLoader()
                text = loader.load(io.BytesIO(content))
            elif filename.endswith(".csv"):
                loader = CSVLoader()
                text = loader.load(io.BytesIO(content))
            elif filename.endswith(".docx"):
                loader = DOCXLoader()
                text = loader.load(io.BytesIO(content))
            else:
                text = content.decode("utf-8", errors="ignore")

            return self._chunk_text(text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract chunks from {filename}: {str(e)}")

    def _chunk_text(self, text: str) -> list:
        chunks = []
        words = text.split()

        current_chunk = []
        current_size = 0

        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1

            if current_size >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                overlap_words = max(1, len(current_chunk) // 4)
                current_chunk = current_chunk[-overlap_words:]
                current_size = sum(len(w) for w in current_chunk) + overlap_words

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return [chunk for chunk in chunks if chunk.strip()]

    async def rebuild_index(self) -> bool:
        return True
