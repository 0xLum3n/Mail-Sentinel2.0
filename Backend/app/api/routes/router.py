"""Top-level API router aggregation."""

from fastapi import APIRouter

from app.api.routes import ai, auth, emails, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(emails.router, prefix="/emails")
api_router.include_router(ai.router, prefix="/ai")
