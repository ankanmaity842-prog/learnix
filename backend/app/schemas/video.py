
from pydantic import BaseModel, ConfigDict, Field


class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    youtube_id: str
    title: str

    description: str | None = None
    channel_name: str | None = None
    url: str
    duration_seconds: int | None = None

    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)

    language: str = "en"
    channel_country: str | None = None

    thumbnail: str | None = None
    thumbnail_has_bengali: bool = False

    difficulty_score: float | None = None
    difficulty_level: str | None = None

    visual_complexity: float | None = None


class VideoSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    language: str = "en"
    level: str = "beginner"
    max_results: int = Field(default=20, ge=1, le=50)


class VideoSearchResponse(BaseModel):
    query: str
    language: str
    level: str
    videos: list[VideoResponse]

    videos: list[VideoResponse]