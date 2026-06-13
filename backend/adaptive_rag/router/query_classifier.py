from pydantic import BaseModel


class ClassificationResult(BaseModel):
    query_type: str
    complexity: str
    needs_docs: bool
    needs_web: bool
    is_time_sensitive: bool
    needs_graph: bool


class QueryClassifier:
    def classify(self, query: str) -> ClassificationResult:
        return ClassificationResult(
            query_type=self._determine_type(query),
            complexity=self._determine_complexity(query),
            needs_docs=self._check_docs_needed(query),
            needs_web=self._check_web_needed(query),
            is_time_sensitive=self._check_time_sensitive(query),
            needs_graph=self._check_graph_needed(query),
        )

    def _determine_type(self, query: str) -> str:
        return "factual"

    def _determine_complexity(self, query: str) -> str:
        return "simple"

    def _check_docs_needed(self, query: str) -> bool:
        return False

    def _check_web_needed(self, query: str) -> bool:
        return False

    def _check_time_sensitive(self, query: str) -> bool:
        return False

    def _check_graph_needed(self, query: str) -> bool:
        return False
