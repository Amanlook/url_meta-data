from fastapi import APIRouter, status

# health router configuration
health_router = APIRouter(prefix="/health", tags=["Health"])


# health check application
@health_router.get("/", summary="Application Health Checkup", status_code=status.HTTP_200_OK)
async def app_health() -> dict:
    """
    ### Application Health check
    This endpoint returns the status of the application.
    """
    return {"status": "ok"}
