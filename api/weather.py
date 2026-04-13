from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from models.schemas import ClosetItem, WeatherRecommendationResponse
from services.weather_service import WeatherService

router = APIRouter(prefix="/api/weather", tags=["weather"])
weather_service = WeatherService()


@router.get("/recommendation", response_model=WeatherRecommendationResponse)
async def get_weather_recommendation(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
) -> WeatherRecommendationResponse:
    """Retrieve live weather and derive a wearable weight recommendation."""

    try:
        weather_data = await weather_service.get_current_weather(lat=lat, lon=lon)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - depends on external API state
        raise HTTPException(status_code=502, detail="Weather provider unavailable") from exc

    temp_c = float(weather_data["main"]["temp"])
    weight = weather_service.temperature_to_weight(temp_c)

    return WeatherRecommendationResponse(
        city=weather_data.get("name", "Unknown"),
        temperature_c=temp_c,
        condition=weather_data["weather"][0]["main"],
        clothing_weight=weight,
    )


@router.post("/filter-closet")
async def filter_closet_for_weather(
    items: list[ClosetItem],
    clothing_weight: Literal["heavy_layers", "mid_layers", "light_layers"] = Query(...),
) -> list[ClosetItem]:
    """Filter the digital closet using server-side weather clothing rules."""

    return weather_service.filter_closet_for_weight(items, clothing_weight)
