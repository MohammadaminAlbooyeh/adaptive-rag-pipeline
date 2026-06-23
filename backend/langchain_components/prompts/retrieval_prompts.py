from langchain_core.prompts import ChatPromptTemplate

RETRIEVAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Use the following context to answer the question."),
        ("human", "Context: {context}\n\nQuestion: {query}"),
    ]
)
