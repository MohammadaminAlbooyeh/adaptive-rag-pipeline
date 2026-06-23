from langchain_core.prompts import ChatPromptTemplate

RELEVANCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Grade whether the document is relevant to the query."),
        ("human", "Document: {document}\n\nQuery: {query}"),
    ]
)

HALLUCINATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Check if the answer is grounded in the provided context."),
        ("human", "Context: {context}\n\nAnswer: {answer}"),
    ]
)
