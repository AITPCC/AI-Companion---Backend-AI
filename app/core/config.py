from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 1000
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    chat_guest_limit: int = 10
    chat_user_limit: int = 30
    chat_window_seconds: int = 86400   
    login_limit: int = 5
    login_window_seconds: int = 900    
    register_limit: int = 5
    register_window_seconds: int = 3600  
    environment: str = "development"
    model_config = SettingsConfigDict(env_file="app/.env")
    database_url: str = (
    "postgresql+psycopg://ai_companion:ai_companion@localhost:5432/ai_companion"
)





@lru_cache
def get_settings():
    return Settings()
