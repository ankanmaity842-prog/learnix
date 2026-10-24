
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Language = Literal["en", "hi", "bn"]
Level = Literal["beginner", "intermediate", "advanced"]


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    video_id: str | int
    title: str

    url: str | None = None
    description: str | None = None
    channel: str | None = None
    thumbnail: str | None = None

    language: Language = "en"

    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)

    channel_country: str | None = None
    is_indian_creator: bool = False

    difficulty: Level | None = None
    level_verified: bool = False

    topic_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    transcript_simplicity: float = Field(default=0.0, ge=0.0, le=1.0)
    visual_simplicity: float = Field(default=0.0, ge=0.0, le=1.0)
    explanation_structure: float = Field(default=0.0, ge=0.0, le=1.0)

    personalization_score: float = Field(
        default=0.0,
        alias="user_match",
        ge=0.0,
        le=1.0,
    )

    duration_score: float = Field(default=0.0, ge=0.0, le=1.0)
    engagement_score: float = Field(default=0.0, ge=0.0, le=1.0)

    final_score: float = Field(
        default=0.0,
        alias="recommendation_score",
        ge=0.0,
        le=1.0,
    )

    reason: str | None = None


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    topic: str = Field(..., min_length=2, max_length=200)
    language: Language = "en"
    level: Level = "beginner"
    limit: int = Field(default=20, ge=1, le=30)
