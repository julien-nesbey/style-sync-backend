from __future__ import annotations

from datetime import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import ClosetItem, get_db


router = APIRouter(prefix="/closet", tags=["closet"])


class ClosetItemCreate(BaseModel):
    """Request to create a closet item."""

    name: str
    category: str = "Uncategorized"
    color_hex: Optional[str] = None
    color_name: Optional[str] = None


class ClosetItemResponse(BaseModel):
    """Closet item response."""

    id: str
    user_id: str
    name: str
    category: str
    color_hex: Optional[str]
    color_name: Optional[str]
    last_worn: datetime
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/{user_id}/items", response_model=ClosetItemResponse)
async def create_closet_item(
    user_id: str,
    request: ClosetItemCreate,
    db: Session = Depends(get_db),
) -> ClosetItemResponse:
    """Add a new item to user's closet."""
    
    item_id = str(uuid.uuid4())
    new_item = ClosetItem(
        id=item_id,
        user_id=user_id,
        name=request.name,
        category=request.category,
        color_hex=request.color_hex,
        color_name=request.color_name,
        last_worn=datetime.utcnow(),
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return ClosetItemResponse.model_validate(new_item)


@router.get("/{user_id}/items", response_model=list[ClosetItemResponse])
async def get_user_closet(
    user_id: str,
    db: Session = Depends(get_db),
) -> list[ClosetItemResponse]:
    """Get all items in user's closet."""
    
    items = db.query(ClosetItem).filter(ClosetItem.user_id == user_id).all()
    
    return [ClosetItemResponse.model_validate(item) for item in items]


@router.get("/{user_id}/items/{item_id}", response_model=ClosetItemResponse)
async def get_closet_item(
    user_id: str,
    item_id: str,
    db: Session = Depends(get_db),
) -> ClosetItemResponse:
    """Get a specific closet item."""
    
    item = (
        db.query(ClosetItem)
        .filter(ClosetItem.id == item_id, ClosetItem.user_id == user_id)
        .first()
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    return ClosetItemResponse.model_validate(item)


@router.put("/{user_id}/items/{item_id}", response_model=ClosetItemResponse)
async def update_closet_item(
    user_id: str,
    item_id: str,
    request: ClosetItemCreate,
    db: Session = Depends(get_db),
) -> ClosetItemResponse:
    """Update a closet item."""
    
    item = (
        db.query(ClosetItem)
        .filter(ClosetItem.id == item_id, ClosetItem.user_id == user_id)
        .first()
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    item.name = request.name
    item.category = request.category
    item.color_hex = request.color_hex
    item.color_name = request.color_name
    item.updated_at = datetime.now()
    
    db.commit()
    db.refresh(item)
    
    return ClosetItemResponse.model_validate(item)


@router.patch("/{user_id}/items/{item_id}/wear", response_model=ClosetItemResponse)
async def mark_item_worn(
    user_id: str,
    item_id: str,
    db: Session = Depends(get_db),
) -> ClosetItemResponse:
    """Mark an item as worn (update last_worn timestamp)."""
    
    item = (
        db.query(ClosetItem)
        .filter(ClosetItem.id == item_id, ClosetItem.user_id == user_id)
        .first()
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    item.last_worn = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return ClosetItemResponse.model_validate(item)


@router.delete("/{user_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_closet_item(
    user_id: str,
    item_id: str,
    db: Session = Depends(get_db),
) -> None:
    """Delete a closet item."""
    
    item = (
        db.query(ClosetItem)
        .filter(ClosetItem.id == item_id, ClosetItem.user_id == user_id)
        .first()
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    db.delete(item)
    db.commit()
