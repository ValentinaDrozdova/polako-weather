import asyncio
from datetime import datetime
from typing import Any, cast

import httpx
from aiocache import cached

from app.config import settings
from app.constants import DEFAULT_CITY, DEFAULT_LAT, DEFAULT_LON
from app.services.city import get_city_name
from app.web.weather.schemas import DailyForecast


@cached(ttl=600)  # type: ignore[untyped-decorator]
async def fetch_weather(*, client: httpx.AsyncClient, lat: float, lon: float) -> dict[str, Any]:
    headers = {"User-Agent": settings.USER_AGENT}
    params = {"lat": lat, "lon": lon}

    response = await client.get(settings.YR_BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    return cast(dict[str, Any], response.json())


def get_daily_forecasts(data: dict[str, Any]) -> list[DailyForecast]:
    results: dict[str, dict[str, Any]] = {}
    timeseries = data["properties"]["timeseries"]

    for entry in timeseries:
        dt = datetime.fromisoformat(entry["time"])
        date_str = dt.date().isoformat()
        hour = dt.hour

        if hour not in (12, 14):
            continue

        if date_str not in results or hour == 14:
            results[date_str] = {
                "date": date_str,
                "temperature": entry["data"]["instant"]["details"]["air_temperature"],
            }

    forecast_objects = [DailyForecast(**item) for item in results.values()]
    return sorted(forecast_objects, key=lambda x: x.date)


class WeatherService:
    async def get_weather_for_location(
        self, lat: float, lon: float, client: httpx.AsyncClient
    ) -> tuple[str, list[DailyForecast]]:
        is_default = lat == DEFAULT_LAT and lon == DEFAULT_LON

        try:
            weather_task = fetch_weather(client=client, lat=lat, lon=lon)

            if is_default:
                raw_weather = await weather_task
                city_name = DEFAULT_CITY
            else:
                city_task = get_city_name(client=client, lat=lat, lon=lon)
                raw_weather, city_name = await asyncio.gather(weather_task, city_task)

            forecast = get_daily_forecasts(raw_weather)
            return city_name, forecast

        except httpx.HTTPError:
            raise
