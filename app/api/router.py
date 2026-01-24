from fastapi import APIRouter

from app.api.routes import chat
from app.api.routes import health

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(health.router)
