from fastapi import FastAPI

from app.api.router import api_router
from app.logger import setup_logging
from app.core.config import get_settings

settings = get_settings()
is_production = settings.environment == "production"

app = FastAPI(
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

app.include_router(api_router)

setup_logging()
