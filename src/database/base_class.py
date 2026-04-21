from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class TimeStampedDocument(Document):
    """
    Abstract base document that adds common fields to all collections.
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        is_root = True

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
