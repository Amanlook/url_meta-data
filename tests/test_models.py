import pytest

from src.url_manager.models import UrlMetaData
from src.url_manager.schema import UrlCreateSchema, UrlMetaDataResponse


class TestUrlCreateSchema:
    def test_valid_url(self):
        schema = UrlCreateSchema(url="https://example.com")  # type: ignore
        assert str(schema.url) == "https://example.com/"

    def test_invalid_url_rejected(self):
        with pytest.raises(Exception):
            UrlCreateSchema(url="not-a-url")  # type: ignore


class TestUrlMetaDataResponse:
    def test_response_fields(self):
        fields = UrlMetaDataResponse.model_fields
        assert "id" in fields
        assert "url" in fields
        assert "headers" in fields
        assert "cookies" in fields
        assert "page_source" in fields
        assert "is_completed" in fields
        assert "created_at" in fields
        assert "updated_at" in fields


class TestUrlMetaDataModel:
    @pytest.mark.asyncio
    async def test_create_document(self):
        doc = UrlMetaData(
            url="https://test.com",
            headers={"content-type": "text/html"},
            cookies={"session": "abc"},
            page_source="<html></html>",
            is_completed=True,
        )
        await doc.insert()

        found = await UrlMetaData.find_one(UrlMetaData.url == "https://test.com")
        assert found is not None
        assert found.url == "https://test.com"
        assert found.is_completed is True
        assert found.headers == {"content-type": "text/html"}

    @pytest.mark.asyncio
    async def test_default_values(self):
        doc = UrlMetaData(url="https://defaults.com")
        await doc.insert()

        found = await UrlMetaData.find_one(UrlMetaData.url == "https://defaults.com")
        assert found is not None
        assert found.headers == {}
        assert found.cookies == {}
        assert found.page_source == ""
        assert found.is_completed is False
