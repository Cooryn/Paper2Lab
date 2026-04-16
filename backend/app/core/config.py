from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = Field(default="Paper2Lab", alias="PAPER2LAB_APP_NAME")
    env: str = Field(default="development", alias="PAPER2LAB_ENV")
    api_prefix: str = Field(default="/api", alias="PAPER2LAB_API_PREFIX")
    database_url: str = Field(
        default="sqlite:///./backend/data/paper2lab.db",
        alias="PAPER2LAB_DATABASE_URL",
    )
    cors_origins: str = Field(default="http://localhost:5173", alias="PAPER2LAB_CORS_ORIGINS")
    log_level: str = Field(default="INFO", alias="PAPER2LAB_LOG_LEVEL")
    enable_online_sources: bool = Field(default=False, alias="PAPER2LAB_ENABLE_ONLINE_SOURCES")
    arxiv_api_url: str = Field(
        default="http://export.arxiv.org/api/query",
        alias="PAPER2LAB_ARXIV_API_URL",
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        alias="PAPER2LAB_OPENAI_BASE_URL",
    )
    openai_api_key: str | None = Field(default=None, alias="PAPER2LAB_OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="PAPER2LAB_OPENAI_MODEL")
    default_timezone: str = Field(default="Asia/Shanghai", alias="PAPER2LAB_DEFAULT_TIMEZONE")
    scheduler_enabled: bool = Field(default=True, alias="PAPER2LAB_SCHEDULER_ENABLED")

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def backend_dir(self) -> Path:
        return ROOT_DIR / "backend"

    @property
    def data_dir(self) -> Path:
        return self.backend_dir / "data"

    @property
    def generated_dir(self) -> Path:
        return self.backend_dir / "generated"

    @property
    def samples_dir(self) -> Path:
        return ROOT_DIR / "samples"

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def normalized_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.generated_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    return settings

