from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde entorno / .env.

    Validación fail-fast: si falta una variable requerida o su tipo es inválido,
    la construcción falla con un error explícito.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "turnos-odontologia"
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"

    database_url: str
    redis_url: str
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("secret_key", mode="before")
    @classmethod
    def _validate_secret_key(cls, value: object) -> str:
        if not value or not isinstance(value, str) or value.strip() == "":
            raise ValueError("SECRET_KEY is required and must not be empty")
        if len(value.strip()) < 32:
            raise ValueError("SECRET_KEY must have at least 32 characters")
        return value

    @field_validator("access_token_expire_minutes", mode="before")
    @classmethod
    def _validate_access_token_expire_minutes(cls, value: object) -> int:
        try:
            minutes = int(value)
        except (ValueError, TypeError):
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer")
        if minutes <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer")
        return minutes


@lru_cache
def get_settings() -> Settings:
    return Settings()