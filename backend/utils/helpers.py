import time
from functools import wraps


def timed(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        return {"result": result, "duration": duration}

    return wrapper


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks
