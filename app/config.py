from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.categories import CATEGORY_VALUES


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://complaints:{env.POSTGRES_PASSWORD}@db:5432/complaints"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "gemma3:1b"
    ollama_timeout_seconds: float = 300
    log_level: str = "INFO"

    # Assignment 2 cascade (assignment2/STEP2.md). Disabled = Assignment 1 single-model behaviour.
    cascade_enabled: bool = False
    cascade_small_model: str = ""
    cascade_large_model: str = ""
    # Comma-separated category names. A ticket escalates when the small model predicts one of them.
    cascade_escalate_on: str = ""
    # Model label returned and stored for every ticket in cascade mode, so callers cannot tell
    # which model answered. Empty = "cascade:<small>><large>".
    cascade_label: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def escalate_on(self) -> frozenset[str]:
        return frozenset(part.strip() for part in self.cascade_escalate_on.split(",") if part.strip())

    @property
    def service_model_label(self) -> str:
        if not self.cascade_enabled:
            return self.ollama_model
        return self.cascade_label or f"cascade:{self.cascade_small_model}>{self.cascade_large_model}"

    @model_validator(mode="after")
    def _check_cascade(self) -> "Settings":
        if not self.cascade_enabled:
            return self
        if not self.cascade_small_model or not self.cascade_large_model:
            raise ValueError("CASCADE_SMALL_MODEL and CASCADE_LARGE_MODEL are required when CASCADE_ENABLED=true")
        unknown = sorted(self.escalate_on - set(CATEGORY_VALUES))
        if unknown:
            raise ValueError(
                f"CASCADE_ESCALATE_ON has unknown categories {unknown}; use the exact names {list(CATEGORY_VALUES)}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

