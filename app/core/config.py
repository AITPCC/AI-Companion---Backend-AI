from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 1000
    model_config = SettingsConfigDict(env_file="app/.env")
    database_url: str = (
    "postgresql+psycopg://ai_companion:ai_companion@localhost:5432/ai_companion"
)





@lru_cache
def get_settings():
    return Settings()
