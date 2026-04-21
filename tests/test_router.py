from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.url_manager.models import UrlMetaData


class TestPostEndpoint:
    @pytest.mark.asyncio
    async def test_create_metadata_success(self, async_client, mock_httpx_response):
        with mock_httpx_response(
            headers={"content-type": "text/html"},
            cookies={"token": "abc"},
            text="<html>test</html>",
        ):
            response = await async_client.post(
                "/api/urls/",
                json={"url": "https://example.com"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com/"
        assert data["is_completed"] is True
        assert data["headers"] == {"content-type": "text/html"}
        assert data["cookies"] == {"token": "abc"}
        assert data["page_source"] == "<html>test</html>"

    @pytest.mark.asyncio
    async def test_create_metadata_duplicate_returns_409(self, async_client):
        doc = UrlMetaData(
            url="https://duplicate.com/",
            headers={"h": "v"},
            cookies={},
            page_source="<html></html>",
            is_completed=True,
        )
        await doc.insert()

        response = await async_client.post(
            "/api/urls/",
            json={"url": "https://duplicate.com"},
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_metadata_invalid_url_returns_422(self, async_client):
        response = await async_client.post(
            "/api/urls/",
            json={"url": "not-a-valid-url"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_metadata_unreachable_url_returns_422(self, async_client):
        with patch("src.url_manager.service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            response = await async_client.post(
                "/api/urls/",
                json={"url": "https://unreachable.com"},
            )
        assert response.status_code == 422
        assert "Connection error" in response.json()["detail"]


class TestGetEndpoint:
    @pytest.mark.asyncio
    async def test_get_existing_metadata_returns_200(self, async_client):
        doc = UrlMetaData(
            url="https://cached.com",
            headers={"server": "nginx"},
            cookies={"id": "1"},
            page_source="<html>cached</html>",
            is_completed=True,
        )
        await doc.insert()

        response = await async_client.get("/api/urls/", params={"url": "https://cached.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://cached.com"
        assert data["is_completed"] is True

    @pytest.mark.asyncio
    async def test_get_missing_metadata_returns_202(self, async_client):
        with patch("src.url_manager.router.collect_metadata_background"):
            response = await async_client.get("/api/urls/", params={"url": "https://new-url.com"})
            assert response.status_code == 202
            data = response.json()
            assert data["detail"] == "Metadata collection has been queued."
            assert data["url"] == "https://new-url.com"

            # Verify a pending record was created
            record = await UrlMetaData.find_one(UrlMetaData.url == "https://new-url.com")
            assert record is not None
            assert record.is_completed is False

    @pytest.mark.asyncio
    async def test_get_pending_metadata_returns_202(self, async_client):
        pending = UrlMetaData(url="https://pending.com", is_completed=False)
        await pending.insert()

        response = await async_client.get("/api/urls/", params={"url": "https://pending.com"})
        assert response.status_code == 202
