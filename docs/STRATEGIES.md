# RAG Strategies

## Overview

The Adaptive RAG Pipeline implements six strategies, each optimized for different types of queries. Strategies are selected automatically by the `StrategySelector` based on query classification, but can also be specified explicitly via the `strategy` field in the API request.

```
Strategy Selection Flow:

QueryClassifier.classify(query)
         |
         v
ClassificationResult:
  - needs_docs: bool
  - needs_web: bool
  - needs_graph: bool
         |
         v
StrategySelector.select(classification)
         |
         v
+------------------+----------------------------------------------------+
| Condition        | Strategy Selected                                   |
+------------------+----------------------------------------------------+
| No retrieval     | direct_llm                                          |
| needs_docs only  | document_rag                                        |
| needs_web only   | web_search_rag                                      |
| needs_docs+web   | hybrid_rag                                          |
| needs_graph      | graph_rag                                           |
| fallback         | self_rag                                            |
+------------------+----------------------------------------------------+
```

---

## 1. DirectLLM Strategy

### When to Use
Simple factual queries that do not require any external context. The LLM answers based entirely on its training knowledge.

### Query Characteristics
- Short, simple questions ("What is the capital of France?")
- Definitions ("Define recursion")
- Common knowledge that does not change ("Who wrote Romeo and Juliet?")
- Any query where `needs_docs`, `needs_web`, and `needs_graph` are all `false`

### How It Works
```
query → llm.generate("Answer the following question:\n\n{query}") → answer
```

### Implementation
```python
class DirectLLMStrategy(BaseStrategy):
    async def execute(self, query: str, **kwargs) -> dict:
        answer = await self.llm.generate(f"Answer the following question:\n\n{query}")
        return {
            "strategy": "direct_llm",
            "query": query,
            "answer": answer,
            "sources": [],
            "documents": [],
        }
```

### Pros and Cons
| Pro | Con |
|-----|-----|
| Fastest strategy (no retrieval) | Limited to LLM training data |
| Lowest latency | No source citations |
| Works offline | Stale or hallucinated information |

### Default Confidence Base: 0.95

---

## 2. DocumentRAG Strategy

### When to Use
Queries that benefit from a private knowledge base of uploaded documents. Best for domain-specific questions where relevant documents have been ingested.

### Query Characteristics
- Domain-specific questions ("What does our Q3 financial report say?")
- Questions about ingested documentation ("Summarize the onboarding guide")
- Queries classified as `needs_docs: true` and `needs_web: false`

### How It Works
```
query → VectorRetriever.retrieve(top_k) → grade relevance (filter < 0.3) →
  build context → llm.generate_with_context(query, context) → answer + sources
```

### Implementation
```python
class DocumentRAGStrategy(BaseStrategy):
    def __init__(self, retriever, llm, grader):
        self.retriever = retriever      # VectorRetriever
        self.llm = llm                  # Any LLM provider
        self.grader = grader            # RelevanceGrader

    async def execute(self, query: str, **kwargs) -> dict:
        docs = await self.retriever.retrieve(query, top_k=kwargs.get("top_k", 5))
        # Filters out documents with relevance_score ≤ 0.3
        filtered_sources = [doc for doc in docs if doc.get("relevance_score", 0) > 0.3]
        context = self._build_context(docs)
        answer = await self.llm.generate_with_context(query, context)
        return {"answer": answer, "sources": filtered_sources, "documents": docs}
```

### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_k` | 5 | Number of documents to retrieve |
| `relevance_threshold` | 0.3 | Minimum relevance score to include as source |

### Pros and Cons
| Pro | Con |
|-----|-----|
| Grounded in your data | Requires documents to be uploaded and indexed |
| Provides cited sources | Slower than DirectLLM due to retrieval |
| Domain-specific accuracy | Depends on embedding quality |

### Default Confidence Base: 0.85

---

## 3. WebSearchRAG Strategy

### When to Use
Time-sensitive queries, current events, or questions about recent information not in the LLM's training data.

### Query Characteristics
- Temporal keywords: "today", "latest", "recent", "current", "breaking", "news"
- Current events ("What happened in the stock market yesterday?")
- Live data ("What is the weather in Tokyo?")
- Queries classified as `needs_web: true` and `needs_docs: false`

### How It Works
```
query → WebRetriever.retrieve(top_k=5) → build context →
  llm.generate_with_context(query, context) → answer + sources
```

### Implementation
```python
class WebSearchStrategy(BaseStrategy):
    def __init__(self, web_retriever, llm):
        self.web_retriever = web_retriever   # WebRetriever (DuckDuckGo)
        self.llm = llm                        # Any LLM provider

    async def execute(self, query: str, **kwargs) -> dict:
        web_results = await self.web_retriever.retrieve(query, top_k=kwargs.get("top_k", 5))
        context = self._build_context(web_results)
        answer = await self.llm.generate_with_context(query, context)
        return {"answer": answer, "sources": web_results, "documents": web_results}
```

### Web Retriever Details
- Uses DuckDuckGo search (`duckduckgo_search` library) by default
- Can be configured to use Google Search via `SEARCH_PROVIDER` environment variable
- Each result contains `body`, `href`, and `title` fields
- Default relevance score assigned: 0.8

### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_k` | 5 | Number of web results to fetch |
| `SEARCH_PROVIDER` | `duckduckgo` | Search engine backend |

### Pros and Cons
| Pro | Con |
|-----|-----|
| Always up-to-date information | Internet connection required |
| No document ingestion needed | Variable source quality |
| Broad knowledge coverage | Slower due to network latency |

### Default Confidence Base: 0.75

---

## 4. HybridRAG Strategy

### When to Use
Queries that benefit from both internal documents AND live web data. Combines the depth of private knowledge with the breadth of web search.

### Query Characteristics
- Complex questions spanning private and public knowledge ("How does our product compare to competitors based on recent reviews?")
- Queries classified as both `needs_docs: true` and `needs_web: true`

### How It Works
```
query → VectorRetriever.retrieve(top_k=3) → doc_results
query → WebRetriever.retrieve(top_k=2)     → web_results

all_results = doc_results + web_results
context = build_context(all_results)
answer = llm.generate_with_context(query, context)

return {answer, sources (truncated to 100 chars), documents}
```

### Implementation
```python
class HybridStrategy(BaseStrategy):
    def __init__(self, doc_retriever, web_retriever, llm):
        self.doc_retriever = doc_retriever     # VectorRetriever
        self.web_retriever = web_retriever     # WebRetriever
        self.llm = llm                         # Any LLM provider

    async def execute(self, query: str, **kwargs) -> dict:
        doc_results = await self.doc_retriever.retrieve(query, top_k=3)
        web_results = await self.web_retriever.retrieve(query, top_k=2)
        all_results = doc_results + web_results
        context = self._build_context(all_results)
        answer = await self.llm.generate_with_context(query, context)
        return {"answer": answer, "sources": all_results[:5], "documents": all_results}
```

### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `doc_top_k` | 3 | Documents to retrieve from vector store |
| `web_top_k` | 2 | Web results to fetch |
| `max_sources` | 5 | Total sources in response |

### Pros and Cons
| Pro | Con |
|-----|-----|
| Best of both worlds (documents + web) | Highest latency (two retrievals) |
| Comprehensive coverage | Sources may be redundant |
| Balanced for complex queries | More tokens consumed |

### Default Confidence Base: 0.80

---

## 5. GraphRAG Strategy

### When to Use
Queries involving entities, relationships, and connections between concepts. Best when the answer requires understanding how entities relate to each other.

### Query Characteristics
- Relationship keywords: "relationship", "connected", "associated", "entity", "entities"
- Entity-focused questions ("What companies does Elon Musk own?")
- Relationship questions ("How is Python related to data science?")
- Queries classified as `needs_graph: true`

### How It Works
```
query → extract entities (uppercase/long words, max 3)
  for each entity → GraphRetriever.retrieve(entity) → relations
  context = build_context(relations)
  answer = llm.generate(prompt with entities + context + query)
```

### Entity Extraction Logic
```python
# In GraphRetriever._extract_entities:
words = query.split()
# Selects words that are:
# 1. Longer than 3 characters AND (uppercase OR starts with uppercase)
# OR falls back to words longer than 3 characters
important_words = [w for w in words if len(w) > 3 and (w.upper() == w or w[0].isupper())]
return important_words[:3]
```

### Implementation
```python
class GraphRAGStrategy(BaseStrategy):
    def __init__(self, graph_retriever, llm):
        self.graph_retriever = graph_retriever   # GraphRetriever(wraps vector_store)
        self.llm = llm                           # Any LLM provider

    async def execute(self, query: str, **kwargs) -> dict:
        graph_results = await self.graph_retriever.retrieve(query, top_k=5)
        context = self._build_context(graph_results)
        answer = await self.llm.generate_with_context(query, context)
        return {"answer": answer, "sources": graph_results, "documents": graph_results}
```

### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_k` | 5 | Results per entity |
| `max_entities` | 3 | Maximum entities to extract from query |

### Pros and Cons
| Pro | Con |
|-----|-----|
| Excellent for relationship questions | Entity extraction is heuristic-based |
| Structured knowledge representation | Limited to vector store data |
| Discovers indirect connections | Not a true knowledge graph (uses vector similarity) |

### Default Confidence Base: 0.70

---

## 6. SelfRAG Strategy

### When to Use
High-stakes queries where answer quality and factual accuracy are critical. SelfRAG iteratively retrieves, critiques, and regenerates answers until quality standards are met.

### Query Characteristics
- Used as fallback when no other strategy clearly matches
- Complex questions requiring verification
- Queries where hallucination prevention is critical

### How It Works
```
iteration = 0
while iteration < max_iterations (3) and no acceptable answer:
    1. RETRIEVE: VectorRetriever.retrieve(current_query, top_k=5)
    2. GRADE: For each doc, RelevanceGrader.grade(doc, query)
       → keep only relevant docs
    3. GENERATE: If relevant docs exist:
         context = build_context(relevant_docs)
         answer = llm.generate_with_context(query, context)
    4. CHECK: HallucinationGrader.grade(answer, context)
         if is_grounded → accept answer, break
         else → rewrite query with "previous answer was incorrect"
    iteration++

if no acceptable answer after max iterations:
    answer = llm.generate(query)  # fallback to direct generation
```

### Implementation
```python
class SelfRAGStrategy(BaseStrategy):
    def __init__(self, retriever, llm, relevance_grader, hallucination_grader):
        self.retriever = retriever               # VectorRetriever
        self.llm = llm                           # Any LLM provider
        self.relevance_grader = relevance_grader # RelevanceGrader
        self.hallucination_grader = hallucination_grader  # HallucinationGrader
        self.max_iterations = 3

    async def execute(self, query: str, **kwargs) -> dict:
        # Iterative retrieve → grade → generate → check hallucination loop
        # Returns on first grounded answer or max iterations
        # Records iteration count in response
```

### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iterations` | 3 | Maximum retrieval-generation cycles |
| `top_k` | 5 | Documents per retrieval |

### Grading Pipeline
1. **RelevanceGrader**: Uses LLM (or keyword overlap fallback) to check if each document is relevant to the query. Only relevant documents are used for generation.
2. **HallucinationGrader**: Uses LLM (or grounding score fallback) to check if the generated answer is factually supported by the retrieved context.

### Pros and Cons
| Pro | Con |
|-----|-----|
| Highest quality assurance | Highest latency (multiple iterations) |
| Self-correcting on hallucination | Token cost multiplier |
| Transparent iteration count | May still fall back to direct generation |

### Default Confidence Base: 0.90

---

## Strategy Comparison

| Strategy | Latency | Accuracy | Freshness | Sources | Config |
|----------|---------|----------|-----------|---------|--------|
| DirectLLM | ★★★★★ Fastest | ★★★ | ★ | None | None needed |
| DocumentRAG | ★★★★ Fast | ★★★★ | ★★★ | Documents | `top_k`, `relevance_threshold` |
| WebSearchRAG | ★★★ Medium | ★★★ | ★★★★★ | Web URLs | `top_k`, `SEARCH_PROVIDER` |
| HybridRAG | ★★ Slow | ★★★★ | ★★★★ | Docs + Web | `doc_top_k`, `web_top_k` |
| GraphRAG | ★★★ Medium | ★★★ | ★★ | Graph | `top_k`, `max_entities` |
| SelfRAG | ★ Slowest | ★★★★★ | ★★★ | Documents | `max_iterations`, `top_k` |

## Forcing a Specific Strategy

Clients can bypass automatic strategy selection by specifying the `strategy` field in the API request:

```json
{
  "text": "What is quantum computing?",
  "strategy": "document_rag",
  "top_k": 3
}
```

This skips the classifier and selector entirely and executes the named strategy directly.
