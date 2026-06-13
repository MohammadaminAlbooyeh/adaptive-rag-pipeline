class ResponseFormatter:
    def format(self, answer: str, sources: list, metadata: dict) -> dict:
        return {
            "answer": answer,
            "sources": sources,
            "metadata": metadata,
        }
