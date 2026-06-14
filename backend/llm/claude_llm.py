from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ClaudeLLM:
    def __init__(self, model: str = "claude-3-opus-20240229", temperature: float = 0):
        self.llm = ChatAnthropic(model=model, temperature=temperature)
        self.model = model

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            raise RuntimeError(f"Claude LLM error: {str(e)}")

    async def generate_with_context(self, prompt: str, context: str) -> str:
        full_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"
        return await self.generate(full_prompt)

    async def grade_relevance(self, document: str, query: str) -> bool:
        prompt = f"""Given a document and a query, determine if the document is relevant to answering the query.

Document: {document}

Query: {query}

Answer with only 'yes' or 'no'."""
        response = await self.generate(prompt)
        return response.strip().lower().startswith("yes")

    async def grade_answer(self, answer: str, context: str) -> bool:
        prompt = f"""Given an answer and its supporting context, determine if the answer is grounded in the context and correct.

Answer: {answer}

Context: {context}

Answer with only 'yes' or 'no'."""
        response = await self.generate(prompt)
        return response.strip().lower().startswith("yes")

    async def detect_hallucination(self, answer: str, context: str) -> bool:
        prompt = f"""Determine if the answer contains hallucinations (claims not supported by context).

Answer: {answer}

Context: {context}

Answer with only 'yes' if there are hallucinations, 'no' if it's grounded."""
        response = await self.generate(prompt)
        return response.strip().lower().startswith("yes")
