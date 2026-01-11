from http import HTTPStatus
from typing import Annotated, cast

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.constants import DEFAULT_LAT, DEFAULT_LON
from app.services.weather import WeatherService
from app.web.weather.schemas import WeatherResponse

router = APIRouter(tags=["weather"])

limiter = Limiter(key_func=get_remote_address)


async def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


@router.get("/weather", status_code=HTTPStatus.OK, response_model=WeatherResponse)
@limiter.limit("10/minute")
async def get_weather(
    request: Request,  # noqa: ARG001
    lat: Annotated[float, Query(ge=-90, le=90)] = DEFAULT_LAT,
    lon: Annotated[float, Query(ge=-180, le=180)] = DEFAULT_LON,
    service: WeatherService = Depends(),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> WeatherResponse:
    try:
        city_name, forecast = await service.get_weather_for_location(lat=lat, lon=lon, client=client)
        return WeatherResponse(city=city_name, forecast=forecast)

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY, detail="Weather provider failed to respond correctly."
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected internal error occurred."
        ) from e
