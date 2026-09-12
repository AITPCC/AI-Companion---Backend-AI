from functools import lru_cache
from ipaddress import ip_network

from pydantic import PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 1000
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    chat_guest_limit: PositiveInt = 10
    chat_user_limit: PositiveInt = 30
    chat_window_seconds: PositiveInt = 86400
    login_limit: PositiveInt = 5
    login_window_seconds: PositiveInt = 900
    register_limit: PositiveInt = 5
    register_window_seconds: PositiveInt = 3600
    guest_source_limit: PositiveInt = 10
    trusted_proxy_cidrs: str = ""
    quota_retention_seconds: PositiveInt = 86400
    environment: str = "development"

    @model_validator(mode="after")
    def validate_proxy_trust(self):
        networks = [
            ip_network(value.strip())
            for value in self.trusted_proxy_cidrs.split(",")
            if value.strip()
        ]
        if any(network.prefixlen == 0 for network in networks):
            raise ValueError("Trust specific proxy networks, never every address")
        if self.environment == "production" and not networks:
            raise ValueError("Production requires verified TRUSTED_PROXY_CIDRS")
        return self

    model_config = SettingsConfigDict(env_file="app/.env")
    database_url: str = (
        "postgresql+psycopg://ai_companion:ai_companion@localhost:5432/ai_companion"
    )


@lru_cache
def get_settings():
    return Settings()
