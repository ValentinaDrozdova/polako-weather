from typing import List

from pydantic import BaseModel


class DailyForecast(BaseModel):
    date: str
    temperature: float


class WeatherResponse(BaseModel):
    city: str
    forecast: List[DailyForecast]
