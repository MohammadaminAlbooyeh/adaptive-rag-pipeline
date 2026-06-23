from langchain_community.llms import Ollama


class LocalLLM:
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.llm = Ollama(model=model, base_url=base_url)
        self.model = model

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.llm.ainvoke(prompt)
            return response
        except Exception as e:
            raise RuntimeError(f"Local LLM error: {str(e)}")

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
