"""
Centralized application configuration.

All values are read from environment variables (see .env.example).
Nothing here should ever be hardcoded for production use — defaults
below are safe ONLY for local development.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Universal AI File Converter"
    ENV: str = "development"  # development | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Database ---
    # Defaults to local SQLite so the app runs with zero external services.
    # In production this should be a postgresql:// URL.
    DATABASE_URL: str = "sqlite:///./dev.db"

    # --- Redis / Celery ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    # When no Redis is available (e.g. quick local dev), conversions run
    # synchronously in-process instead of via Celery. Never set this true
    # in production — it blocks the request thread.
    RUN_TASKS_EAGERLY: bool = True

    # --- Storage ---
    STORAGE_BACKEND: str = "local"  # local | s3
    LOCAL_STORAGE_PATH: str = "./storage_data"
    MAX_UPLOAD_SIZE_MB: int = 200

    # S3 (only required when STORAGE_BACKEND=s3)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    AWS_S3_ENDPOINT_URL: str = ""  # set for S3-compatible providers (e.g. R2, MinIO)

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
