from langchain_core.prompts import ChatPromptTemplate

ROUTING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a query routing assistant. Classify the query and select the best RAG strategy.",
        ),
        ("human", "{query}"),
    ]
)
