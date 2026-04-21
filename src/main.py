from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.constants import Environment
from src.core.database import init_db
from src.core.health import health_router
from src.url_manager.router import router as url_manager_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


# Create a FastAPI App for META Urls Manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="META Urls Manager",
    openapi_url=f"{settings.API_URL}/openapi.json",
    docs_url=f"{settings.API_URL}/docs",
    debug=settings.ENVIRONMENT == Environment.LOCAL,
    lifespan=lifespan,
)


# Add CORS middleware if allowed origins are set
if settings.ALLOWED_CORS_ORIGINS:
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=[str(url).rstrip("/") for url in settings.ALLOWED_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Include the API routers with the specified prefix
app.include_router(router=health_router, prefix=settings.API_URL)
app.include_router(router=url_manager_router, prefix=settings.API_URL)
