from typing import Annotated

from beanie import Indexed
from pydantic import Field

from src.database.base_class import TimeStampedDocument


class UrlMetaData(TimeStampedDocument):
    url: Annotated[str, Indexed(unique=True)]
    headers: dict = Field(default_factory=dict)
    cookies: dict = Field(default_factory=dict)
    page_source: str = Field(default="")
    is_completed: bool = Field(default=False)

    class Settings:
        name = "url_metadata"
