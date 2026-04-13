from __future__ import annotations

from fastapi import APIRouter

from models.schemas import (
    ClosetUtilizationRequest,
    ClosetUtilizationResponse,
    StyleAnalyticsResponse,
)
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/closet-utilization", response_model=ClosetUtilizationResponse)
async def closet_utilization(
    payload: ClosetUtilizationRequest,
) -> ClosetUtilizationResponse:
    """Return the sustainability metric: % of closet worn in 6 months."""

    return AnalyticsService.closet_utilization(
        payload.items,
        reference_date=payload.reference_date,
    )


@router.post("/style-report", response_model=StyleAnalyticsResponse)
async def style_report(payload: ClosetUtilizationRequest) -> StyleAnalyticsResponse:
    """Return a richer dashboard payload with utilization + color usage."""

    return AnalyticsService.style_report(
        payload.items,
        reference_date=payload.reference_date,
    )
