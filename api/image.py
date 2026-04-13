from __future__ import annotations
import base64

from fastapi import APIRouter

from models.schemas import ColorMatchResponse, ImageProcessResponse, ImageProcessRequest, ColorMatchRequest
from services.image_processing import ImageService

router = APIRouter(prefix="/api/image", tags=["image"])
image_service = ImageService()

@router.post("/process", response_model=ImageProcessResponse)
async def process_image(
    request: ImageProcessRequest
) -> ImageProcessResponse:
    """Remove background + extract dominant colors for a wardrobe photo upload from base64 string."""

    # Remove possible data URI prefix block like data:image/jpeg;base64,
    if "," in request.base64_image:
        request.base64_image = request.base64_image.split(",")[1]

    image_bytes = base64.b64decode(request.base64_image)
    cleaned_bytes = image_service.remove_background(image_bytes)
    colors = image_service.extract_dominant_colors(cleaned_bytes)

    description = "Dominant tones: " + ", ".join(c.name for c in colors)
    transparent_base64 = (
        image_service.to_base64_png(cleaned_bytes) if request.include_transparent_image else None
    )

    return ImageProcessResponse(
        dominant_colors=colors,
        accessible_description=description,
        transparent_image_base64=transparent_base64,
    )


@router.post("/match", response_model=ColorMatchResponse)
async def match_two_items(
    request: ColorMatchRequest
) -> ColorMatchResponse:
    """Run color extraction on two garments and return an accessibility-first match line."""

    if "," in request.item_a_base64:
        request.item_a_base64 = request.item_a_base64.split(",")[1]
    if "," in request.item_b_base64:
        request.item_b_base64 = request.item_b_base64.split(",")[1]

    a_bytes = image_service.remove_background(base64.b64decode(request.item_a_base64))
    b_bytes = image_service.remove_background(base64.b64decode(request.item_b_base64))

    a_color = image_service.extract_dominant_colors(a_bytes, n_colors=1)[0]
    b_color = image_service.extract_dominant_colors(b_bytes, n_colors=1)[0]

    return ColorMatchResponse(
        item_a=a_color,
        item_b=b_color,
        accessible_match_text=image_service.describe_pair(a_color, b_color),
    )
