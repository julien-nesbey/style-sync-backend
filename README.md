# Style-Sync Backend (Engine)

FastAPI service for image intelligence, weather orchestration, and closet analytics.

## Stack

- FastAPI (async)
- Pydantic v2 models
- rembg for garment background removal
- scikit-learn K-Means for dominant color extraction
- OpenWeatherMap integration via httpx
- python-multipart for image upload endpoints

## Run With uv

```bash
uv sync
uv run uvicorn main:app --reload --port 8000
```

Set environment variables before weather calls:

```bash
export OPENWEATHER_API_KEY="your_key_here"
```

## API Surface

- `POST /api/image/process`: removes background and returns dominant colors + accessibility text
- `POST /api/image/match`: compares two uploaded items and returns color-blind-friendly pairing text
- `GET /api/weather/recommendation?lat=...&lon=...`: returns weather and clothing weight recommendation
- `POST /api/weather/filter-closet?clothing_weight=...`: weather-aware closet filtering
- `POST /api/analytics/closet-utilization`: percentage of items worn in the last 6 months
- `POST /api/analytics/style-report`: utilization plus top color usage slices for dashboard charts

## Architecture Notes

- `services/image_processing.py` contains the ML pipeline. Background removal is run first to reduce noise before K-Means clustering.
- `services/weather_service.py` handles external weather calls and converts temperature into `heavy_layers` / `mid_layers` / `light_layers`.
- `services/analytics_service.py` computes sustainability metrics and chart-ready usage aggregates.
