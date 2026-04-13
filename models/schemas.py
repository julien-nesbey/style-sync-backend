from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DominantColor(BaseModel):
    """A dominant color extracted by K-Means from a clothing image."""

    hex: str = Field(description="Hex color code in #RRGGBB format")
    name: str = Field(description="Human-readable color name for accessibility")
    ratio: float = Field(ge=0.0, le=1.0, description="Pixel share for the color")


class ImageProcessRequest(BaseModel):
    """Input payload containing a base64 encoded photo."""
    base64_image: str
    include_transparent_image: bool = True

class ColorMatchRequest(BaseModel):
    """Input payload containing two base64 encoded photos."""
    item_a_base64: str
    item_b_base64: str

class ImageProcessResponse(BaseModel):
    """Response payload after image cleanup + color extraction."""

    dominant_colors: list[DominantColor]
    accessible_description: str
    transparent_image_base64: str | None = Field(
        default=None,
        description="Optional base64 encoded PNG with removed background",
    )


class ColorMatchResponse(BaseModel):
    """Response payload for matching two garments by dominant colors."""

    item_a: DominantColor
    item_b: DominantColor
    accessible_match_text: str


class WeatherRecommendationResponse(BaseModel):
    """Current weather info paired with clothing weight guidance."""

    city: str
    temperature_c: float
    condition: str
    clothing_weight: Literal["heavy_layers", "mid_layers", "light_layers"]


class ClosetItem(BaseModel):
    """A wardrobe item tracked by the digital closet."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    category: str
    tags: list[str] = Field(default_factory=list)
    color_hex: str | None = None
    color_name: str | None = None
    last_worn: datetime | None = None


class ClosetUtilizationRequest(BaseModel):
    """Input for sustainability-oriented closet utilization analytics."""

    items: list[ClosetItem]
    reference_date: date | None = None


class ClosetUtilizationResponse(BaseModel):
    """Summary metrics for usage in the past 6 months."""

    worn_items: int
    total_items: int
    utilization_percent: float
    dormant_items: int


class ColorUsageSlice(BaseModel):
    """Aggregated color usage slice for dashboard charts."""

    label: str
    count: int


class StyleAnalyticsResponse(BaseModel):
    """Combined analytics payload for frontend chart dashboards."""

    closet_utilization: ClosetUtilizationResponse
    color_usage_top: list[ColorUsageSlice]
