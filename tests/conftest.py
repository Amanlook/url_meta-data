import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from src.main import app
from src.url_manager.models import UrlMetaData


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def init_test_db():
    """Initialize a mock MongoDB for each test and clean up after."""
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["test_db"],  # type: ignore
        document_models=[UrlMetaData],
    )
    yield
    await UrlMetaData.delete_all()


@pytest.fixture
async def async_client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_httpx_response():
    """Patch httpx to return a fake response instead of making real HTTP calls."""

    def _mock(
        status_code: int = 200,
        headers: dict | None = None,
        cookies: dict | None = None,
        text: str = "<html><body>test</body></html>",
    ):
        mock_response = AsyncMock()
        mock_response.status_code = status_code
        mock_response.headers = headers or {"content-type": "text/html"}
        mock_cookies = MagicMock()
        mock_cookies.items.return_value = (cookies or {}).items()
        mock_response.cookies = mock_cookies
        mock_response.text = text

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        return patch("src.url_manager.service.httpx.AsyncClient", return_value=mock_client)

    return _mock
