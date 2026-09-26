from pydantic import BaseModel, ConfigDict


class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    youtube_id: str
    title: str
    description: str | None = None
    channel_name: str | None = None
    url: str
    duration_seconds: int | None = None
    difficulty_score: float | None = None
    difficulty_level: str | None = None
    visual_complexity: float | None = None


class VideoSearchRequest(BaseModel):
    query: str
    language: str = "en"
    max_results: int = 10


class VideoSearchResponse(BaseModel):
    query: str
    language: str
    videos: list[VideoResponse]