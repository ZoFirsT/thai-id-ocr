from functools import lru_cache
from typing import Dict, List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised application configuration using type-safe settings."""

    app_name: str = "Thai ID Card OCR API"
    environment: str = Field(default="development", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    ollama_base_url: AnyHttpUrl = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL")
    llm_enabled: bool = Field(default=True, alias="LLM_ENABLED")

    max_file_size_mb: int = Field(default=8, alias="MAX_FILE_SIZE_MB")
    pii_masking_enabled: bool = Field(default=True, alias="PII_MASKING_ENABLED")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/backend.log", alias="LOG_FILE")
    log_to_console: bool = Field(default=True, alias="LOG_TO_CONSOLE")

    class Config:
        env_file = None
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


BACKEND_CONFIG_DEFAULTS: Dict[str, str] = {
    "APP_ENV": "development",
    "API_V1_PREFIX": "/api/v1",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    # "OLLAMA_MODEL": "qwen2.5",
    "OLLAMA_MODEL": "qwen2.5:3b",
    "LLM_ENABLED": "true",
    "MAX_FILE_SIZE_MB": "8",
    "PII_MASKING_ENABLED": "true",
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "logs/backend.log",
    "LOG_TO_CONSOLE": "true",
}


FRONTEND_CONFIG_DEFAULTS: Dict[str, str] = {
    "NEXT_PUBLIC_API_BASE_URL": "http://localhost:8000",
    "NEXT_PUBLIC_MAX_UPLOAD_MB": "8",
}
