from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Literature review verification agent with retrieval, rule-based checks, and optional LLM judging.",
)
app.include_router(router)
