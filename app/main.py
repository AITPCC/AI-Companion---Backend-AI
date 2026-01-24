from fastapi import FastAPI

from app.api.router import api_router
from app.logger import setup_logging

app = FastAPI()

app.include_router(api_router)

setup_logging()
