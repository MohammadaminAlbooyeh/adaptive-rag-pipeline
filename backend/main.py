from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.utils.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.APP_NAME}")


@app.on_event("shutdown")
async def shutdown():
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}
