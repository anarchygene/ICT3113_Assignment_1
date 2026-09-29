from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://complaints:{env.POSTGRES_PASSWORD}@db:5432/complaints"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "gemma3:1b"
    ollama_timeout_seconds: float = 300
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

