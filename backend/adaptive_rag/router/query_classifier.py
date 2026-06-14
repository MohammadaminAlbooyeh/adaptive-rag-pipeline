from pydantic import BaseModel


class ClassificationResult(BaseModel):
    query_type: str
    complexity: str
    needs_docs: bool
    needs_web: bool
    is_time_sensitive: bool
    needs_graph: bool


class QueryClassifier:
    def __init__(self):
        self.keywords_factual = {"what", "when", "where", "who", "which", "how many", "define"}
        self.keywords_exploratory = {"why", "explain", "describe", "tell me about"}
        self.keywords_comparative = {"compare", "versus", "vs", "difference", "different", "better", "worse"}
        self.keywords_procedural = {"how", "steps", "instructions", "guide", "process"}
        self.keywords_opinion = {"think", "believe", "should", "recommend", "best", "worst"}
        self.keywords_temporal = {"today", "yesterday", "latest", "recent", "now", "current", "breaking", "news"}
        self.keywords_graph = {"relationship", "connected", "associated", "entity", "entities"}

    def classify(self, query: str) -> ClassificationResult:
        query_lower = query.lower()
        return ClassificationResult(
            query_type=self._determine_type(query_lower),
            complexity=self._determine_complexity(query_lower),
            needs_docs=self._check_docs_needed(query_lower),
            needs_web=self._check_web_needed(query_lower),
            is_time_sensitive=self._check_time_sensitive(query_lower),
            needs_graph=self._check_graph_needed(query_lower),
        )

    def _determine_type(self, query: str) -> str:
        if any(kw in query for kw in self.keywords_comparative):
            return "comparative"
        elif any(kw in query for kw in self.keywords_procedural):
            return "procedural"
        elif any(kw in query for kw in self.keywords_exploratory):
            return "exploratory"
        elif any(kw in query for kw in self.keywords_opinion):
            return "opinion"
        else:
            return "factual"

    def _determine_complexity(self, query: str) -> str:
        words = len(query.split())
        conjunctions = sum(1 for word in query.split() if word in {"and", "or", "but"})

        if words > 20 or conjunctions >= 2:
            return "complex"
        elif words > 10 or conjunctions == 1:
            return "moderate"
        else:
            return "simple"

    def _check_docs_needed(self, query: str) -> bool:
        no_doc_keywords = {"current", "latest", "today", "breaking", "recent news"}
        if any(kw in query for kw in no_doc_keywords):
            return False
        if any(kw in query for kw in self.keywords_temporal):
            return False
        return True

    def _check_web_needed(self, query: str) -> bool:
        return any(kw in query for kw in self.keywords_temporal)

    def _check_time_sensitive(self, query: str) -> bool:
        return any(kw in query for kw in self.keywords_temporal)

    def _check_graph_needed(self, query: str) -> bool:
        return any(kw in query for kw in self.keywords_graph)
