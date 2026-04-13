from __future__ import annotations

import os
from typing import Literal

import httpx

from models.schemas import ClosetItem


ClothingWeight = Literal["heavy_layers", "mid_layers", "light_layers"]


class WeatherService:
    """External weather orchestration + clothing-weight recommendation logic."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "")

    async def get_current_weather(self, lat: float, lon: float) -> dict:
        """Fetch current weather from OpenWeatherMap for GPS coordinates."""

        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY is not configured")

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }
        url = "https://api.openweathermap.org/data/2.5/weather"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def temperature_to_weight(temp_c: float) -> ClothingWeight:
        """Map temperature bands to wardrobe weight categories."""

        if temp_c <= 12:
            return "heavy_layers"
        if temp_c <= 24:
            return "mid_layers"
        return "light_layers"

    @staticmethod
    def filter_closet_for_weight(
        items: list[ClosetItem], clothing_weight: ClothingWeight
    ) -> list[ClosetItem]:
        """Filter closet candidates based on weather-driven weight recommendation."""

        rule_map = {
            "heavy_layers": {"coat", "sweater", "hoodie", "jacket", "wool"},
            "mid_layers": {"shirt", "chino", "cardigan", "jeans"},
            "light_layers": {"shorts", "linen", "tank", "tee", "dress"},
        }
        accepted = rule_map[clothing_weight]

        def item_matches(item: ClosetItem) -> bool:
            checks = {item.category.lower(), *[t.lower() for t in item.tags]}
            return bool(checks.intersection(accepted))

        return [item for item in items if item_matches(item)]
