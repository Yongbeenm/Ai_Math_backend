"""
Central application configuration.

Everything environment-specific (database URL, CORS, debug mode) lives here
so the rest of the codebase never reads os.environ directly. This is what
lets the same code run unchanged in local development, CI, and later on a
real server.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Khmer Math Lab API"
    app_version: str = "0.1.0"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    # Comma-free JSON list, e.g. ["*"] for local dev or
    # ["https://your-flutter-app-domain"] once you have one.
    cors_origins: list[str] = ["*"]

    # aiosqlite for local dev on the M3 Pro. Swap for a Postgres URL later
    # (e.g. "postgresql+asyncpg://...") without touching any other file.
    database_url: str = "sqlite+aiosqlite:///./khmer_math_lab.db"
    
    # Math Vision / OCR provider: "stub", "tesseract", "kiri" (khmer_ocr), "mathpix", "google", or "gemini"
    vision_provider: str = "stub"
    
    # Gemini API credentials (if using gemini vision provider)
    gemini_api_key: str | None = None

    # Mathpix credentials (if using mathpix provider)
    mathpix_app_id: str | None = None
    mathpix_app_key: str | None = None
    
    # Google Vision credentials path (if using google provider)
    google_application_credentials: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() -> os.environ parsing only happens once."""
    return Settings()
