# LangGraph Workflows

## Overview

LangGraph workflows provide **state machine orchestration** for complex, multi-step RAG processes. Unlike the simpler strategy-based execution in `strategies/`, LangGraph workflows use explicit state schemas, graph-based node routing, and conditional edges with guardrails (iteration limits, fallback paths).

All workflows use `langgraph.graph.StateGraph` and are compiled with `workflow.compile()`. Each implements a `run(query)` async method that returns a structured result.

```
Common Pattern:

  ENTRY POINT
      |
      v
  +---------+     conditional      +----------+
  |  Node A +--------------------> |  Node B  |
  +----+----+     /        \      +----+-----+
       |        /            \          |
       v      /              \         v
  +---------+                 +----------+
  |  Node D |                 |  Node C  |
  +---------+                 +----------+
       |
       v
      END
```

---

## 1. AdaptiveWorkflow

### Purpose
Full end-to-end adaptive RAG pipeline with classification, strategy routing, document retrieval, relevance grading, answer generation, answer grading, query rewriting, and web search fallback. The most comprehensive workflow — covers all possible paths.

### State Schema

```python
class WorkflowState(TypedDict):
    query: str              # Current query (may be rewritten)
    query_type: str         # Classification result ("factual", "exploratory", etc.)
    strategy: str           # Selected strategy name
    documents: list         # Retrieved documents from vector store
    web_results: list       # Retrieved web search results
    answer: str             # Generated answer
    grade: str              # Document relevance grade ("relevant" / "not_relevant")
    answer_quality: str     # Answer quality ("good" / "hallucination" / "not_useful")
    generation_count: int   # Number of answer generations (guards against infinite loops)
    web_search_count: int   # Number of web searches performed
```

### State Diagram

```
                             START
                               |
                               v
                    +---------------------+
                    |   classify_query    |
                    |  (QueryClassifier)  |
                    +----------+----------+
                               |
                conditional    |
               +--------------+--------------+
               |                             |
         "simple"                      "complex"
               |                             |
               v                             v
        +-------------+             +-------------+
        | route_query |             | route_query |
        | (set        |             | (set        |
        |  strategy)  |             |  strategy)  |
        +------+------+             +------+------+
               |                           |
               +----------+----------------+
                          |
                          v
                 +-----------------------+
                 |  retrieve_documents   |
                 | (VectorRetriever,     |
                 |  guard: max 3 gen)    |
                 +----------+------------+
                            |
                            v
                 +-----------------------+
                 |   grade_documents     |
                 | (RelevanceGrader for  |
                 |  each document)       |
                 +----------+------------+
                            |
               conditional  |
            +---------------+---------------+
            |                               |
       "relevant"                     "not_relevant"
            |                               |
            v                               v
    +----------------+           +--------------------+
    | generate_answer|           |  rewrite_query     |
    | (ContextBuilder|           | (QueryRewriter,    |
    |  + LLM gen)    |           |  guard: max 3 gen) |
    +-------+--------+           +---------+----------+
            |                              |
            |                              |
            |    (if rewritten)            |
            |    +-------------------------+
            |    |
            v    v
    +-----------------------+
    |    grade_answer       |
    | (HallucinationGrader |
    |  + AnswerGrader)      |
    +----------+------------+
               |
    conditional|
    +----------+----------+----------+
    |          |          |          |
 "good"  "hallucination"  |   "not_useful"
    |          |          |          |
    v          |          |          v
   END         |          |   +-------------+
               |          |   | web_search  |
               |          |   | (max 3      |
               |          |   |  searches)  |
               |          |   +------+------+
               |          |          |
               +----+-----+          |
                    |                |
                    v                |
         +-------------------+      |
         | generate_answer   |      |
         | (retry with       |      |
         |  hallucinated     |      |
         |  answer fixed)    |      |
         +-------------------+      |
                    |               |
                    v               |
              +-----------+         |
              | grade_answer| <-----+
              +-----+------+
                    |
               (loops until good
                or max iterations)

    MAX ITERATIONS GUARD:
    - generation_count >= 3 → skip retrieval, generate with llm only
    - web_search_count >= 3 → skip web search, use existing results
    - generation_count >= 3 in grade_documents → force "relevant"
```

### Nodes

| Node | Function | Description |
|------|----------|-------------|
| `classify_query` | `_classify_query` | Runs `QueryClassifier.classify(query)`. Sets `query_type` and `strategy` in state. |
| `route_query` | `_route_query` | Passes the strategy forward. Entry point for conditioning on classification. |
| `retrieve_documents` | `_retrieve_documents` | Calls `VectorRetriever.retrieve(query, top_k=5)`. Guarded by `generation_count < 3`. |
| `grade_documents` | `_grade_documents` | Grades each document with `RelevanceGrader`. If any document is relevant, returns `"relevant"`, else `"not_relevant"`. |
| `generate_answer` | `_generate_answer` | Builds context from `documents + web_results` via `ContextBuilder`. Calls `AnswerGenerator.generate` if context exists, else `llm.generate` directly. |
| `grade_answer` | `_grade_answer` | Runs `HallucinationGrader` and `AnswerGrader`. Returns `"good"`, `"hallucination"`, or `"not_useful"`. |
| `rewrite_query` | `_rewrite_query` | Calls `QueryRewriter.rewrite(query, feedback)`. Guarded by `generation_count < 3`. Falls back to appending "(refined)". |
| `web_search` | `_web_search` | Calls `WebRetriever.retrieve(query, top_k=3)`. Guarded by `web_search_count < 3`. |

### Decision Functions

| Function | Condition | Returns |
|----------|-----------|---------|
| `_decide_route` | Always | `"simple"` (both paths merge at `route_query`) |
| `_decide_grade` | `grade == "relevant"` OR `generation_count >= 3` | `"relevant"` → `generate_answer` |
| | otherwise | `"not_relevant"` → `rewrite_query` |
| `_decide_answer_quality` | `answer_quality == "good"` | `"good"` → `END` |
| | `answer_quality == "hallucination"` | `"hallucination"` → `generate_answer` (retry) |
| | `answer_quality == "not_useful"` | `"not_useful"` → `web_search` |

### Execution

```python
workflow = AdaptiveWorkflow(llm, vector_store)
result = await workflow.run("What is the impact of climate change on agriculture?")
# result contains: answer, sources, metadata (strategy, query_type, confidence)
```

---

## 2. SelfRAGWorkflow

### Purpose
Iterative self-reflection loop: retrieve documents, reflect on their relevance, rewrite the query if needed, then generate. The self-reflection node explicitly critiques each document and rewrites the query to improve retrieval quality.

### State Schema

```python
class SelfRAGState(TypedDict):
    query: str          # Current query (may be rewritten by reflection)
    documents: list     # Retrieved documents
    reflection: str     # Reflection notes on document relevance
    answer: str         # Generated answer
    iteration: int      # Current iteration count (max 3)
```

### State Diagram

```
  START
    |
    v
+----------+
| retrieve | ← VectorRetriever.retrieve(query, top_k=5)
+----+-----+     Guard: iteration >= max_iterations (3) → skip
     |
     | conditional
     | (always goes to "reflect" unless max iterations)
     v
+----------+
| reflect  | ← For each doc: RelevanceGrader.grade(doc, query)
+----+-----+     If not relevant, add to reflection_notes
     |           If any reflection_notes, rewrite query with feedback
     v
+----------+
| generate | ← ContextBuilder.build(documents)
+----+-----+   → AnswerGenerator.generate(query, context)
     |
     v
    END
```

### Nodes

| Node | Function | Description |
|------|----------|-------------|
| `retrieve` | `_retrieve` | Retrieves documents. Guarded by `iteration < max_iterations`. Increments iteration. |
| `reflect` | `_reflect` | Grades each document for relevance. Collects notes on non-relevant documents. Rewrites query if feedback exists. |
| `generate` | `_generate` | Builds context from documents, generates answer. Falls back to direct LLM if no context. |

### Decision Functions

| Function | Condition | Returns |
|----------|-----------|---------|
| `_decide` | `iteration >= max_iterations` | `"generate"` (skip reflection, generate with whatever was retrieved) |
| | otherwise | `"reflect"` |

### Key Behaviors

- Query rewriting in `_reflect` uses `QueryRewriter` with LLM: "Rewrite the following query to be more specific and searchable, given feedback about non-relevant documents."
- If LLM rewrite returns the same query, the original query is preserved.
- Reflection notes are accumulated as a semicolon-separated string.

### Execution

```python
workflow = SelfRAGWorkflow(llm, vector_store)
result = await workflow.run("Explain quantum entanglement")
# result contains: query, documents, reflection, answer, iteration
```

---

## 3. CorrectiveRAGWorkflow

### Purpose
Retrieve documents, grade their relevance collectively, and if the average relevance is too low, correct by supplementing with web search results. This workflow is designed for queries where internal documents may be insufficient.

### State Schema

```python
class CorrectiveRAGState(TypedDict):
    query: str             # Original query
    documents: list        # Retrieved documents from vector store
    grade: str             # Collective relevance grade ("correct" / "generate")
    corrected_docs: list   # Documents + web results after correction
    answer: str            # Generated answer
```

### State Diagram

```
  START
    |
    v
+----------+
| retrieve | ← VectorRetriever.retrieve(query, top_k=5)
+----+-----+
     |
     v
+----------+
|   grade  | ← For each doc: RelevanceGrader.grade(doc, query)
+----+-----+     Compute average relevance score
     |           avg_score >= 0.5 → "generate"
     |           avg_score < 0.5  → "correct"
     | conditional
     +--------+--------+
     |                 |
"correct"         "generate"
     |                 |
     v                 |
+----------+           |
| correct  |           |
| (web     |           |
|  search  |           |
|  fallback)           |
+----+-----+           |
     |                 |
     v                 v
+-----------------------+
|       generate        | ← ContextBuilder.build(corrected_docs or documents)
+-----------+-----------+   → AnswerGenerator.generate(query, context)
            |
            v
           END
```

### Nodes

| Node | Function | Description |
|------|----------|-------------|
| `retrieve` | `_retrieve` | `VectorRetriever.retrieve(query, top_k=5)`. |
| `grade` | `_grade` | Grades each document with `RelevanceGrader`. Computes average score. If `avg_score < 0.5`, returns `"correct"`, else `"generate"`. |
| `correct` | `_correct` | Web search fallback: `WebRetriever.retrieve(query, top_k=3)`. Deduplicates by source URL to avoid overlap with existing docs. Merges new web results into `corrected_docs`. |
| `generate` | `_generate` | Uses `corrected_docs` if available, else original `documents`. Generates answer via `AnswerGenerator`. Falls back to direct LLM if no context. |

### Decision Functions

| Function | Condition | Returns |
|----------|-----------|---------|
| `_decide` | `grade == "correct"` | `"correct"` → supplement with web search |
| | otherwise | `"generate"` → proceed with current documents |

### Key Behaviors

- Deduplication in `_correct`: sources already present in documents are excluded from web results (matched by `source` URL).
- No iteration limit (single pass). If documents are relevant, generate immediately. If not, correct once with web search and generate.

### Execution

```python
workflow = CorrectiveRAGWorkflow(llm, vector_store)
result = await workflow.run("What are the side effects of this medication?")
# result contains: query, documents, grade, corrected_docs, answer
```

---

## 4. GraphRAGWorkflow

### Purpose
Extract named entities from the query, traverse a knowledge graph (via vector similarity per entity), and generate an answer using the relationship context. Best for queries about entities and their connections.

### State Schema

```python
class GraphRAGState(TypedDict):
    query: str          # Original query
    entities: list      # Extracted entity names
    relations: list     # Retrieved relationship documents
    answer: str         # Generated answer
```

### State Diagram

```
  START
    |
    v
+------------------+
| extract_entities | ← Heuristic entity extraction from query
+--------+---------+     Words: len > 3 AND (is_upper OR starts_upper)
         |               Fallback: words with len > 3 (first 3 max)
         |               Sets state.entities = ["Entity1", "Entity2", ...]
         v
+------------------+
| traverse_graph   | ← For each entity:
+--------+---------+     GraphRetriever.retrieve(entity, top_k=3)
         |               Collects relationship documents into state.relations
         v
+------------------+
|     generate     | ← Builds prompt with entities, context, and query
+--------+---------+   → llm.generate(prompt)
         |             Falls back to AnswerGenerator if no context
         v
        END
```

### Nodes

| Node | Function | Description |
|------|----------|-------------|
| `extract_entities` | `_extract_entities` | Extracts entities from query using heuristic: words that are uppercase, start with uppercase, or longer than 3 characters. Max 3 entities. |
| `traverse_graph` | `_traverse_graph` | For each entity, calls `GraphRetriever.retrieve(entity, top_k=3)`. Handles both dict and Document object returns. |
| `generate` | `_generate` | Builds a custom prompt with entities listed and graph context included. Generates answer via LLM. Falls back to `AnswerGenerator` if no relations found. |

### Entity Extraction Logic

```python
# In GraphRAGWorkflow._extract_entities:
words = query.split()
entities = []
for w in words:
    cleaned = w.strip('.,!?;:()[]{}"\'')
    if len(cleaned) > 3 and (cleaned[0].isupper() or cleaned.isupper()):
        entities.append(cleaned)
if not entities:
    entities = [w for w in words if len(w) > 3][:3]
return {"entities": entities}
```

### Generation Prompt

When context is available, the prompt format is:

```
Based on the knowledge graph context below, answer the query.

Entities: {entity1}, {entity2}

Context:
{retrieved_relation_documents}

Query: {original_query}

Answer:
```

### Execution

```python
workflow = GraphRAGWorkflow(llm, vector_store)
result = await workflow.run("How are Tesla and SpaceX connected?")
# result contains: answer, sources, metadata (entities list)
```

---

## Workflow Comparison

| Aspect | AdaptiveWorkflow | SelfRAGWorkflow | CorrectiveRAGWorkflow | GraphRAGWorkflow |
|--------|-----------------|-----------------|----------------------|-----------------|
| **Nodes** | 8 | 3 | 4 | 3 |
| **Max Iterations** | 3 (generation + web) | 3 | 1 (single pass) | 1 (single pass) |
| **Query Rewriting** | Yes | Yes | No | No |
| **Web Fallback** | Yes (on "not_useful") | No | Yes (on low relevance) | No |
| **Grading** | Relevance + Hallucination + Answer | Relevance only | Relevance only (collective) | None |
| **Best For** | General purpose, unknown queries | High-accuracy requirements | Document-heavy with web fallback | Entity/relationship queries |
| **Complexity** | High | Medium | Medium | Low |

## Shared Components

All workflows use these components from the `generator/` and `graders/` modules:

- **AnswerGenerator** (`generator/answer_generator.py`): Builds query+context prompt and calls LLM.
- **ContextBuilder** (`generator/context_builder.py`): Joins document contents with double newlines.
- **ResponseFormatter** (`generator/response_formatter.py`): Structures final answer with sources and metadata.
- **RelevanceGrader** (`graders/relevance_grader.py`): LLM-based or heuristic document relevance scoring.
- **HallucinationGrader** (`graders/hallucination_grader.py`): LLM-based or heuristic grounding check.
- **AnswerGrader** (`graders/answer_grader.py`): Heuristic answer quality scoring.

## Guardrails

All iterative workflows implement max-iteration guards to prevent infinite loops:

```
if generation_count >= max_iterations:
    skip retrieval, generate answer directly
if web_search_count >= max_iterations:
    skip web search, use existing results
if iteration >= max_iterations:
    force "generate" / "relevant" to break the loop
```

The `max_iterations` defaults are:
- **AdaptiveWorkflow**: 3 (generation + web search each)
- **SelfRAGWorkflow**: 3 (total iterations)
- **CorrectiveRAGWorkflow**: 1 (single pass, no loop)
- **GraphRAGWorkflow**: 1 (linear pipeline, no loop)
