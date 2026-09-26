from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    preferred_language: str = Field(
        default="en",
        pattern="^(en|bn|hi)$",
    )


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    preferred_language: str | None = Field(
        default=None,
        pattern="^(en|bn|hi)$",
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    preferred_language: str
    is_active: bool
    created_at: datetime