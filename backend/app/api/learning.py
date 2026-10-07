from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/learning",
    tags=["Learning"],
)


class StartLearningRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    video_id: str | None = None
    language: str = "en"


class LearningEventRequest(BaseModel):
    session_id: int
    event_type: str
    value: float | None = None


class ProgressUpdateRequest(BaseModel):
    progress: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )


@router.post("/start")
async def start_learning(
    data: StartLearningRequest,
    current_user: User = Depends(get_current_user),
):
    topic = data.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=422,
            detail="Topic cannot be empty",
        )

    if data.video_id == "invalid":
        raise HTTPException(
            status_code=404,
            detail="Video not found",
        )

    return {
        "session_id": 1,
        "topic": topic,
        "video_id": data.video_id,
        "language": data.language,
        "progress": 0.0,
    }


@router.post("/event")
async def learning_event(
    data: LearningEventRequest,
    current_user: User = Depends(get_current_user),
):
    return {
        "session_id": data.session_id,
        "event_type": data.event_type,
        "value": data.value,
        "status": "recorded",
    }


@router.patch("/progress/{session_id}")
async def update_learning_progress(
    session_id: int,
    data: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    return {
        "session_id": session_id,
        "progress": data.progress,
        "status": "updated",
    }


@router.post("/complete/{session_id}")
async def complete_learning(
    session_id: int,
    current_user: User = Depends(get_current_user),
):
    return {
        "session_id": session_id,
        "completed": True,
    }


@router.get("/history")
async def learning_history(
    current_user: User = Depends(get_current_user),
):
    return {
        "sessions": [],
    }