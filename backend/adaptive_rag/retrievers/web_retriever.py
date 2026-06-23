from typing import List
from backend.adaptive_rag.retrievers.base_retriever import BaseRetriever
from duckduckgo_search import DDGS
import asyncio


class WebRetriever(BaseRetriever):
    def __init__(self):
        self.ddgs = DDGS()

    async def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._sync_retrieve, query, top_k
            )
            return results
        except Exception as e:
            raise RuntimeError(f"Web retrieval failed: {str(e)}")

    def _sync_retrieve(self, query: str, top_k: int) -> List[dict]:
        try:
            results = list(self.ddgs.text(query, max_results=top_k))
            formatted_results = []

            for result in results:
                formatted_results.append(
                    {
                        "content": f"{result.get('body', '')}",
                        "source": result.get("href", ""),
                        "title": result.get("title", ""),
                        "relevance_score": 0.8,
                    }
                )

            return formatted_results
        except Exception as e:
            raise RuntimeError(f"DuckDuckGo search failed: {str(e)}")
