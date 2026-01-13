import httpx
from aiocache import cached

from app.config import settings


@cached(ttl=3600)  # type: ignore[untyped-decorator]
async def get_city_name(*, client: httpx.AsyncClient, lat: float, lon: float) -> str:
    params: dict[str, str | float] = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 10,
        "accept-language": "en",
    }
    headers = {"User-Agent": settings.USER_AGENT}

    try:
        resp = await client.get(settings.MAP_BASE_URL, params=params, headers=headers, timeout=5.0)
        resp.raise_for_status()
        address = resp.json().get("address", {})
        return address.get("city") or address.get("town") or address.get("village") or "Unknown"
    except Exception:
        return "Custom Location"
