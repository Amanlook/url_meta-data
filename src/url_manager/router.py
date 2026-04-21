from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse

from src.url_manager.crud import url_metadata_crud
from src.url_manager.models import UrlMetaData
from src.url_manager.schema import UrlCreateSchema, UrlMetaDataResponse
from src.url_manager.service import UrlFetchError, collect_metadata_background, fetch_and_store_metadata

router = APIRouter(prefix="/urls", tags=["URL Metadata"])


@router.post(
    "/",
    response_model=UrlMetaDataResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_url_metadata(payload: UrlCreateSchema):
    """Fetch metadata for a URL and store it in MongoDB."""
    url = str(payload.url)

    existing = await url_metadata_crud.get_by_url(url)
    if existing and existing.is_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Metadata for this URL already exists.",
        )

    try:
        record = await fetch_and_store_metadata(url)
    except UrlFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    return record


@router.get(
    "/",
    response_model=UrlMetaDataResponse,
    responses={202: {"description": "Metadata collection queued"}},
)
async def get_url_metadata(url: str, background_tasks: BackgroundTasks):
    """
    Retrieve metadata for a URL.
    Returns 200 with data if it exists, or 202 if collection has been queued.
    """
    record = await url_metadata_crud.get_by_url(url)

    if record and record.is_completed:
        return record

    if not record:
        pending = UrlMetaData(url=url, is_completed=False)
        await pending.insert()

    background_tasks.add_task(collect_metadata_background, url)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"detail": "Metadata collection has been queued.", "url": url},
    )
