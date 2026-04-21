import logging

import httpx

from src.url_manager.crud import url_metadata_crud
from src.url_manager.models import UrlMetaData

logger = logging.getLogger(__name__)


class UrlFetchError(Exception):
    """Raised when fetching a URL fails."""

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch {url}: {reason}")


async def fetch_and_store_metadata(url: str) -> UrlMetaData:
    """Fetch headers, cookies, and page source from a URL and store in MongoDB."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url)
    except httpx.TimeoutException:
        raise UrlFetchError(url, "Request timed out")
    except httpx.InvalidURL:
        raise UrlFetchError(url, "Invalid URL format")
    except httpx.RequestError as exc:
        raise UrlFetchError(url, f"Connection error: {exc}")

    headers = dict(response.headers)
    cookies = {k: v for k, v in response.cookies.items()}
    page_source = response.text

    record = await url_metadata_crud.get_by_url(url)
    if record:
        await record.set(
            {
                "headers": headers,
                "cookies": cookies,
                "page_source": page_source,
                "is_completed": True,
            }
        )
        return record

    obj = UrlMetaData(
        url=url,
        headers=headers,
        cookies=cookies,
        page_source=page_source,
        is_completed=True,
    )
    await obj.insert()
    return obj


async def collect_metadata_background(url: str) -> None:
    """Background task: fetch metadata for a URL that was not in the DB."""
    try:
        await fetch_and_store_metadata(url)
        logger.info("Background metadata collection completed for %s", url)
    except UrlFetchError:
        logger.exception("Background metadata collection failed for %s", url)
    except Exception:
        logger.exception("Unexpected error during background collection for %s", url)
