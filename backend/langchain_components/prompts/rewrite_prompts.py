from langchain.prompts import ChatPromptTemplate

REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the query to be more specific and searchable."),
    ("human", "Original: {query}\n\nRewritten:"),
])
