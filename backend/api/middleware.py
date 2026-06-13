import time
from fastapi import Request
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")
    return response
