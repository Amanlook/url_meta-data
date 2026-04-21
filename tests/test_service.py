from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.url_manager.models import UrlMetaData
from src.url_manager.service import UrlFetchError, fetch_and_store_metadata


class TestFetchAndStoreMetadata:
    @pytest.mark.asyncio
    async def test_creates_new_record(self, mock_httpx_response):
        with mock_httpx_response(
            headers={"content-type": "text/html"},
            cookies={"sid": "123"},
            text="<html>hello</html>",
        ):
            result = await fetch_and_store_metadata("https://example.com")

        assert result.url == "https://example.com"
        assert result.headers == {"content-type": "text/html"}
        assert result.cookies == {"sid": "123"}
        assert result.page_source == "<html>hello</html>"
        assert result.is_completed is True

    @pytest.mark.asyncio
    async def test_updates_existing_record(self, mock_httpx_response):
        existing = UrlMetaData(url="https://update.com", is_completed=False)
        await existing.insert()

        with mock_httpx_response(
            headers={"server": "nginx"},
            cookies={},
            text="<html>updated</html>",
        ):
            result = await fetch_and_store_metadata("https://update.com")

        assert result.is_completed is True
        assert result.page_source == "<html>updated</html>"

    @pytest.mark.asyncio
    async def test_timeout_raises_url_fetch_error(self):
        with patch(
            "src.url_manager.service.httpx.AsyncClient",
        ) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(UrlFetchError, match="timed out"):
                await fetch_and_store_metadata("https://slow.com")

    @pytest.mark.asyncio
    async def test_connection_error_raises_url_fetch_error(self):
        with patch(
            "src.url_manager.service.httpx.AsyncClient",
        ) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(UrlFetchError, match="Connection error"):
                await fetch_and_store_metadata("https://down.com")
