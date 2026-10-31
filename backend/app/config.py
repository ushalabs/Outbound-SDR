from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore", populate_by_name=True,
                                      hide_input_in_errors=True)
    database_url: SecretStr
    direct_database_url: SecretStr
    gemini_api_key: SecretStr
    gemini_model: str
    embedding_model: str | None = None
    embedding_dimensions: int = Field(default=768, ge=128, le=3072)
    app_env: str = Field(default="development", validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"))
    demo_mode: bool = False
    enable_real_email_sending: bool = Field(
        default=False, validation_alias=AliasChoices("ENABLE_REAL_EMAIL_SENDING", "ENABLE_REAL_SENDING")
    )

    @field_validator("database_url", "direct_database_url")
    @classmethod
    def postgres_only(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
            raise ValueError("A PostgreSQL connection URL is required")
        return value

    @field_validator("gemini_api_key")
    @classmethod
    def nonempty_secret(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("GEMINI_API_KEY is required")
        return value

    @field_validator("enable_real_email_sending")
    @classmethod
    def sending_disabled(cls, value: bool) -> bool:
        if value:
            raise ValueError("Real email sending must remain disabled for this application")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
