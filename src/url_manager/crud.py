from src.database.crud_base import CRUDBase
from src.url_manager.models import UrlMetaData
from src.url_manager.schema import UrlCreateSchema, UrlMetaDataUpdateSchema


class CRUDUrlMetaData(CRUDBase[UrlMetaData, UrlCreateSchema, UrlMetaDataUpdateSchema]):
    async def get_by_url(self, url: str) -> UrlMetaData | None:
        return await self.model.find_one(self.model.url == url)


url_metadata_crud = CRUDUrlMetaData(UrlMetaData)
