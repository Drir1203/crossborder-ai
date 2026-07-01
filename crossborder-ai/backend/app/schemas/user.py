"""VeyaShip - User Schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: Optional[str] = None
    credits: int
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
