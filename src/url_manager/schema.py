from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, HttpUrl


class UrlCreateSchema(BaseModel):
    url: HttpUrl


class UrlMetaDataUpdateSchema(BaseModel):
    headers: dict | None = None
    cookies: dict | None = None
    page_source: str | None = None
    is_completed: bool | None = None


class UrlMetaDataResponse(BaseModel):
    id: PydanticObjectId
    url: str
    headers: dict
    cookies: dict
    page_source: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime
