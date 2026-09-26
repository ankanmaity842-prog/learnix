from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):

    video_id: int
    title: str
    url: str | None = None

    topic_relevance: float = 0.0
    transcript_simplicity: float = 0.0
    visual_simplicity: float = 0.0
    explanation_structure: float = 0.0

    personalization_score: float = Field(
        default=0.0,
        alias="user_match",
    )

    duration_score: float = 0.0
    engagement_score: float = 0.0

    final_score: float = Field(
        default=0.0,
        alias="recommendation_score",
    )

    reason: str | None = None

    model_config = {
        "populate_by_name": True,
    }


class RecommendationRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=2,
    )

    language: str = "en"

    level: str = "beginner"

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
    )