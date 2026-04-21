from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.url_manager.models import UrlMetaData

DOCUMENT_MODELS: list = [UrlMetaData]


async def init_db() -> None:
    client = AsyncIOMotorClient(settings.MONGO.uri)
    await init_beanie(
        database=client[settings.MONGO.DB],  # type: ignore[arg-type]
        document_models=DOCUMENT_MODELS,
    )
