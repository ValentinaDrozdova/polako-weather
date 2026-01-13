import asyncio
from datetime import datetime, time
from typing import Any, cast
from zoneinfo import ZoneInfo

import httpx
from aiocache import cached
from timezonefinder import TimezoneFinder

from app.config import settings
from app.constants import DEFAULT_CITY, DEFAULT_LAT, DEFAULT_LON
from app.services.city import get_city_name
from app.web.weather.schemas import DailyForecast

tf = TimezoneFinder()


def get_timezone(*, lat: float, lon: float) -> ZoneInfo:
    """Determine the timezone based on coordinates."""
    tz_name = tf.timezone_at(lng=lon, lat=lat)
    return ZoneInfo(tz_name) if tz_name else ZoneInfo("UTC")


def parse_to_local(*, utc_str: str, tz: ZoneInfo) -> datetime:
    utc_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return utc_dt.astimezone(tz)


def interpolate_temperature(points: list[tuple[datetime, float]], target_dt: datetime) -> float:
    """Calculate temperature using linear interpolation."""
    for dt, temp in points:
        if dt == target_dt:
            return temp

    before = [p for p in points if p[0] < target_dt]
    after = [p for p in points if p[0] > target_dt]

    if before and after:
        p1_dt, p1_temp = before[-1]
        p2_dt, p2_temp = after[0]

        # Linear interpolation formula
        total_diff = (p2_dt - p1_dt).total_seconds()
        target_diff = (target_dt - p1_dt).total_seconds()

        return p1_temp + (p2_temp - p1_temp) * (target_diff / total_diff)

    if before:
        return before[-1][1]
    if after:
        return after[0][1]

    raise ValueError("Not enough data points to determine temperature.")


def get_daily_forecasts(data: dict[str, Any]) -> list[DailyForecast]:
    timeseries = data["properties"]["timeseries"]
    lon, lat = data["geometry"]["coordinates"][:2]
    tz = get_timezone(lat=lat, lon=lon)

    daily_points: dict[str, list[tuple[datetime, float]]] = {}
    for entry in timeseries:
        local_dt = parse_to_local(utc_str=entry["time"], tz=tz)
        date_str = local_dt.date().isoformat()
        temp = entry["data"]["instant"]["details"]["air_temperature"]

        daily_points.setdefault(date_str, []).append((local_dt, temp))

    results = []
    for date_str, points in daily_points.items():
        points.sort(key=lambda x: x[0])

        # Target time is 14:00 local time
        target_dt = datetime.combine(points[0][0].date(), time(14, 0)).replace(tzinfo=tz)

        try:
            final_temp = interpolate_temperature(points, target_dt)
            results.append(DailyForecast(date=date_str, temperature=round(final_temp, 1)))
        except ValueError:
            continue

    return sorted(results, key=lambda x: x.date)


@cached(ttl=600)  # type: ignore[untyped-decorator]
async def fetch_weather(*, client: httpx.AsyncClient, lat: float, lon: float) -> dict[str, Any]:
    headers = {"User-Agent": settings.USER_AGENT}
    params = {"lat": lat, "lon": lon}

    response = await client.get(settings.YR_BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    return cast(dict[str, Any], response.json())


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
