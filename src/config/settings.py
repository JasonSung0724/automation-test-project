from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENV: Literal["dev", "staging", "prod"] = Field(default="dev")

    # URLs
    BASE_URL: str = Field(default="https://dev.mrsplitter.com")
    API_BASE_URL: str = Field(default="")

    # Auth
    AUTH_TOKEN: str = Field(default="")
    TEST_KEY: str = Field(default="")

    # Browser
    BROWSER: Literal["chromium", "firefox", "webkit"] = Field(default="chromium")
    HEADLESS: bool = Field(default=True)
    SLOW_MO: int = Field(default=0, ge=0)
    TIMEOUT: int = Field(default=5000, description="Default timeout in ms")

    # Viewport
    VIEWPORT_WIDTH: int = Field(default=1280)
    VIEWPORT_HEIGHT: int = Field(default=720)

    # Locale
    LOCALE: Literal["en", "zh-TW", "th", "ja"] = Field(default="en")

    # Test User (new user, created per session)
    TEST_USER_DISPLAY_NAME: str = Field(default="E2E Bot")

    # Old User (fixed, persists across runs)
    OLD_USER_TOKEN: str = Field(default="")
    OLD_USER_ID: str = Field(default="")
    OLD_USER_DISPLAY_NAME: str = Field(default="Old E2E Bot")

    def model_post_init(self, __context) -> None:
        if not self.API_BASE_URL:
            self.API_BASE_URL = f"{self.BASE_URL}/api"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
