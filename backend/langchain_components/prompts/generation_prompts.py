from langchain.prompts import ChatPromptTemplate

GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer the question using the provided context."),
    ("human", "Context: {context}\n\nQuestion: {query}"),
])
