from functools import lru_cache

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import Environment


class MongoSettings(BaseSettings):
    USER: str = ""
    PASSWORD: str = ""
    DB: str = ""
    HOST: str = "db"
    PORT: int = 27017

    @property
    def uri(self) -> str:
        return f"mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}"


class Settings(BaseSettings):
    """Application settings for META Urls Manager."""

    PROJECT_NAME: str = "META Urls Manage"
    PROJECT_DESCRIPTION: str = "META Urls Manage Backend API"

    # the route for api docs and all endpoints
    API_URL: str = "/api"

    # The current environment
    ENVIRONMENT: Environment = Environment.LOCAL

    # List of allowed CORS origins
    ALLOWED_CORS_ORIGINS: list[HttpUrl] = []

    # MongoDB settings
    MONGO: MongoSettings = MongoSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Retrieves and caches the application settings.
    """
    return Settings()  # type: ignore


settings = get_settings()
