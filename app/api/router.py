from fastapi import APIRouter

from app.api.routes import auth
from app.api.routes import chat
from app.api.routes import health
from app.api.routes import users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(health.router)
api_router.include_router(users.router)
