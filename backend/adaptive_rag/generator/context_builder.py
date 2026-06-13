from typing import List


class ContextBuilder:
    def build(self, documents: List[dict]) -> str:
        return "\n\n".join(doc.get("content", "") for doc in documents)
