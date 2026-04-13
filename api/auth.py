from __future__ import annotations

from datetime import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import User, get_db, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


class UserSignupRequest(BaseModel):
    """Signup request payload."""

    email: EmailStr
    password: str
    name: str


class UserLoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response payload."""

    id: str
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/signup", response_model=UserResponse)
async def signup(
    request: UserSignupRequest, db: Session = Depends(get_db)
) -> UserResponse:
    """Create a new user account."""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=UserResponse)
async def login(
    request: UserLoginRequest, db: Session = Depends(get_db)
) -> UserResponse:
    """Authenticate user and return user info."""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    return UserResponse.model_validate(user)


@router.get("/me/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)) -> UserResponse:
    """Get current user info."""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)
