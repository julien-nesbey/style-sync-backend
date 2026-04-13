from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta

from models.schemas import (
    ClosetItem,
    ClosetUtilizationResponse,
    ColorUsageSlice,
    StyleAnalyticsResponse,
)


class AnalyticsService:
    """Compute sustainability + style behavior metrics for dashboards."""

    @staticmethod
    def closet_utilization(
        items: list[ClosetItem], reference_date: date | None = None
    ) -> ClosetUtilizationResponse:
        """Compute what percentage of items were worn in the past 6 months."""

        now = reference_date or date.today()
        # Create a naive datetime for calculation
        cutoff = datetime.combine(now, datetime.min.time()) - timedelta(days=180)

        total = len(items)
        # Strip timezone info from last_worn (which comes from JS as ISO 8601 with Z) before comparing
        worn = sum(1 for item in items if item.last_worn and item.last_worn.replace(tzinfo=None) >= cutoff)
        dormant = max(total - worn, 0)
        utilization = round((worn / total) * 100, 2) if total else 0.0

        return ClosetUtilizationResponse(
            worn_items=worn,
            total_items=total,
            utilization_percent=utilization,
            dormant_items=dormant,
        )

    @staticmethod
    def color_usage(items: list[ClosetItem], top_n: int = 6) -> list[ColorUsageSlice]:
        """Aggregate wearable color frequency for frontend pie/bar charts."""

        counts: Counter[str] = Counter(
            (item.color_name or "Unspecified") for item in items
        )
        return [
            ColorUsageSlice(label=color, count=count)
            for color, count in counts.most_common(top_n)
        ]

    @classmethod
    def style_report(
        cls, items: list[ClosetItem], reference_date: date | None = None
    ) -> StyleAnalyticsResponse:
        """Combine utilization + color usage into one API-friendly payload."""

        utilization = cls.closet_utilization(items, reference_date=reference_date)
        colors = cls.color_usage(items)
        return StyleAnalyticsResponse(closet_utilization=utilization, color_usage_top=colors)
