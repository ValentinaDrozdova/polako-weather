from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI

from app.config import settings
from app.web.weather.routes import router as weather_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    client = httpx.AsyncClient(timeout=httpx.Timeout(5.0))
    app.state.http_client = client
    yield
    await client.aclose()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_TITLE,
        description="Service for tracking weather at 14:00",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.include_router(weather_router, prefix="/api")

    return application
