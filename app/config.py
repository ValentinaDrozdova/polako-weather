from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Polako Weather"
    USER_AGENT: str = "PolakoWeatherApp/1.0 (contact: example@email.com)"
    YR_BASE_URL: str = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    MAP_BASE_URL: str = "https://nominatim.openstreetmap.org/reverse"


settings = Settings()
