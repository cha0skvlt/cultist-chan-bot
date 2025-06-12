"""Configuration loader."""

from __future__ import annotations

from pathlib import Path
import yaml
from pydantic_settings import BaseSettings

CONFIG_FILE = Path(__file__).with_name("config.yaml")


class Settings(BaseSettings):
    """Application settings."""

    TELEGRAM_TOKEN: str = ""
    DB_PATH: str = "bot.db"
    LLM_URL: str = "http://localhost:8000/generate"
    MEMORY_PATH: str = "memory.json"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config() -> Settings:
    """Return populated settings object."""
    data = {}
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open() as fh:
            data = yaml.safe_load(fh) or {}
    return Settings(**data)

