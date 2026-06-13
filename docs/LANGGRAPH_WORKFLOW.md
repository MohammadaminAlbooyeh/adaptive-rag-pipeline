# LangGraph Workflow

## Main Adaptive Workflow

Nodes: classify_query, route_query, retrieve_documents, grade_documents, generate_answer, grade_answer, rewrite_query, web_search

Edges: Conditional routing with retry loops for poor retrieval or hallucination.
