from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies import get_current_user
from app.models.learning_session import LearningSession
from app.models.video import Video
from app.models.topic import Topic
from app.models.user import User


router = APIRouter(
    prefix="/learning",
    tags=["Learning"],
)


class StartLearningRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    video_id: Optional[str] = None
    language: str = "en"


class LearningEvent(BaseModel):
    session_id: int
    event_type: str
    timestamp: Optional[float] = None
    value: Optional[float] = None


class LearningProgressUpdate(BaseModel):
    watch_percentage: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )
    watch_time_seconds: Optional[int] = Field(
        default=None,
        ge=0,
    )
    quiz_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )


@router.post("/start")
async def start_learning(
    data: StartLearningRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    topic_name = data.topic.strip()

    if not topic_name:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    video = None

    if data.video_id:
        video = (
            db.query(Video)
            .filter(Video.video_id == data.video_id.strip())
            .first()
        )

        if not video:
            raise HTTPException(
                status_code=404,
                detail="Video not found",
            )

    topic = (
        db.query(Topic)
        .filter(Topic.name.ilike(topic_name))
        .first()
    )

    session = LearningSession(
        user_id=current_user.id,
        video_id=video.id if video else None,
        topic_id=topic.id if topic else None,
        watch_percentage=0.0,
        watch_time_seconds=0,
        quiz_score=None,
        completed=False,
        started_at=datetime.utcnow(),
        language=data.language,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "topic": topic_name,
        "video_id": data.video_id,
        "video_db_id": video.id if video else None,
        "topic_id": topic.id if topic else None,
        "language": session.language,
        "completed": session.completed,
        "started_at": session.started_at,
    }


@router.post("/event")
async def record_learning_event(
    data: LearningEvent,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(LearningSession)
        .filter(
            LearningSession.id == data.session_id,
            LearningSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Learning session not found",
        )

    event_type = data.event_type.strip().lower()

    if not event_type:
        raise HTTPException(
            status_code=400,
            detail="Event type cannot be empty",
        )

    if event_type == "video_completed":
        session.watch_percentage = 100.0

    elif event_type == "watch_progress":
        if data.value is not None:
            session.watch_percentage = max(
                0.0,
                min(float(data.value), 100.0),
            )

    elif event_type == "watch_time":
        if data.value is not None:
            session.watch_time_seconds = max(
                0,
                int(data.value),
            )

    elif event_type == "quiz_completed":
        if data.value is not None:
            session.quiz_score = max(
                0.0,
                min(float(data.value), 100.0),
            )

    elif event_type == "learning_completed":
        session.completed = True
        session.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "event_type": event_type,
        "value": data.value,
        "watch_percentage": session.watch_percentage,
        "watch_time_seconds": session.watch_time_seconds,
        "quiz_score": session.quiz_score,
        "completed": session.completed,
        "status": "recorded",
    }


@router.patch("/progress/{session_id}")
async def update_learning_progress(
    session_id: int,
    data: LearningProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(LearningSession)
        .filter(
            LearningSession.id == session_id,
            LearningSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Learning session not found",
        )

    if data.watch_percentage is not None:
        session.watch_percentage = data.watch_percentage

    if data.watch_time_seconds is not None:
        session.watch_time_seconds = data.watch_time_seconds

    if data.quiz_score is not None:
        session.quiz_score = data.quiz_score

    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "watch_percentage": session.watch_percentage,
        "watch_time_seconds": session.watch_time_seconds,
        "quiz_score": session.quiz_score,
        "completed": session.completed,
    }


@router.post("/complete/{session_id}")
async def complete_learning(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(LearningSession)
        .filter(
            LearningSession.id == session_id,
            LearningSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Learning session not found",
        )

    session.completed = True
    session.watch_percentage = max(
        session.watch_percentage,
        100.0,
    )
    session.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "completed": session.completed,
        "watch_percentage": session.watch_percentage,
        "completed_at": session.completed_at,
    }


@router.get("/history")
async def learning_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(LearningSession)
        .filter(
            LearningSession.user_id == current_user.id
        )
        .order_by(
            LearningSession.started_at.desc()
        )
        .limit(50)
        .all()
    )

    results = []

    for session in sessions:
        video = session.video
        topic = session.topic

        results.append(
            {
                "session_id": session.id,
                "topic": (
                    topic.name
                    if topic
                    else None
                ),
                "video_id": (
                    video.video_id
                    if video
                    else None
                ),
                "video_db_id": (
                    video.id
                    if video
                    else None
                ),
                "language": session.language,
                "watch_percentage": (
                    session.watch_percentage
                ),
                "watch_time_seconds": (
                    session.watch_time_seconds
                ),
                "quiz_score": session.quiz_score,
                "completed": session.completed,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
            }
        )

    return {
        "sessions": results
    }