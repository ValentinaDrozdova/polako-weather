# Polako Weather API Service

This is a simple FastAPI service that provides weather forecasts. It is optimized to show the temperature in the middle of the day.

### How it works
* **Target Time**: The service looks for a forecast at **14:00**. If that time is not available (common in long-term forecasts), it picks **12:00** instead.
* **Data Source**: It uses the Norwegian Meteorological Institute (MET Norway) API.
* **Default Location**: If you don't provide coordinates, the service defaults to **Belgrade** (Lat: 44.8125, Lon: 20.4612).

---

### Getting Started

**Local Setup (Poetry):**
1. Install dependencies:  
   `poetry install`
2. Start the server:  
   `make run` (or `poetry run uvicorn app.app:app --reload`)

**Docker Setup:**
```bash
  docker build -t polako-weather .
  docker run -p 8000:8000 polako-weather
```

### Interactive Documentation
Once the service is running, you can access the interactive Swagger UI documentation at:  
**http://localhost:8000/docs**

---

### API Endpoints

#### GET `/api/weather`
Returns a list of daily temperature forecasts.

**Query Parameters:**
* `lat` (float, optional) — Latitude. Default: 44.8125 (Belgrade).
* `lon` (float, optional) — Longitude. Default: 20.4612 (Belgrade).

**Example Response:**
```json
{
  "city": "Belgrade",
  "forecast": [
    {
      "date": "2026-01-15",
      "temperature": 15.0
    }
  ]
}
```

---

## Development

The project enforces strict typing and code quality standards.

* **Linting**: Controlled via **Ruff** and **Mypy** (Strict mode).

### Useful Commands

* `make lint` – Run code quality checks.