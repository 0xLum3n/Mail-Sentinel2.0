from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routes.router import api_router
from app.core.config import get_settings
from app.db.postgres import dispose_engine
from app.db.redis import close_redis
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import add_error_handlers
from app.middleware.request_id import RequestIDMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting Mail Sentinel backend")
    yield
    await close_redis()
    await dispose_engine()
    logger.info("Mail Sentinel backend stopped")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered email security, phishing detection, forensic analysis, and SOC platform.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

add_cors_middleware(app)
app.add_middleware(RequestIDMiddleware)
add_error_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)
