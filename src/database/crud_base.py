from typing import Any, Generic, Sequence, Type, TypeVar

from beanie import Document, PydanticObjectId
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Document)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations using Beanie (MongoDB).
    Extend this for specific document model CRUD classes.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def get(self, id: PydanticObjectId) -> ModelType | None:
        """Get a specific document by id."""
        return await self.model.get(id)

    async def filter(
        self,
        *,
        sort_by: str | None = "-created_at",
        offset: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[ModelType]:
        """
        Get multiple documents with optional filtering, sorting, and pagination.
        Args:
            sort_by: Field to sort by (prefix with '-' for descending). Defaults to '-created_at'.
            offset: Number of documents to skip. Defaults to 0.
            limit: Maximum number of documents to retrieve. Defaults to 10.
            filters: Dictionary of field-value pairs to filter on. Defaults to None.
        """
        query = self.model.find(filters or {})
        if sort_by:
            query = query.sort(sort_by)
        return await query.skip(offset).limit(limit).to_list()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new document with provided input data."""
        db_obj = self.model(**obj_in.model_dump())
        await db_obj.insert()
        return db_obj

    async def update(self, *, id: PydanticObjectId, obj_in: UpdateSchemaType) -> ModelType | None:
        """Update a specific document by id."""
        db_obj = await self.model.get(id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        await db_obj.set(update_data)
        return db_obj

    async def delete(self, *, id: PydanticObjectId) -> None:
        """Delete a specific document by id."""
        db_obj = await self.model.get(id)
        if not db_obj:
            return None
        await db_obj.delete()
