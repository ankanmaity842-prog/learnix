from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.models.video import Video
from app.models.topic import Topic
from app.models.learning_session import LearningSession
from app.models.progress import Progress


router = APIRouter(
    prefix="/learning",
    tags=["Learning"],
)


class StartLearningRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
    )

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


# =========================================================
# START LEARNING
# =========================================================

@router.post("/start")
async def start_learning(
    data: StartLearningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic_name = data.topic.strip()

    if not topic_name:
        raise HTTPException(
            status_code=422,
            detail="Topic cannot be empty",
        )

    # -----------------------------------------------------
    # Find or create topic
    # -----------------------------------------------------

    topic = (
        db.query(Topic)
        .filter(
            Topic.name.ilike(topic_name)
        )
        .first()
    )

    if not topic:
        topic = Topic(
            name=topic_name,
            difficulty_level="beginner",
        )

        db.add(topic)
        db.flush()

    # -----------------------------------------------------
    # Find video
    # -----------------------------------------------------

    video = None

    if data.video_id:
        video = (
            db.query(Video)
            .filter(
                Video.youtube_id == data.video_id
            )
            .first()
        )

        if not video:
            raise HTTPException(
                status_code=404,
                detail="Video not found in database",
            )

    else:
        # A learning session requires a video.
        raise HTTPException(
            status_code=400,
            detail="video_id is required",
        )

    # -----------------------------------------------------
    # Create session
    # -----------------------------------------------------

    session = LearningSession(
        user_id=current_user.id,
        video_id=video.id,
        topic_id=topic.id,
        watch_percentage=0.0,
        watch_time_seconds=0,
        completed=False,
        language=data.language,
    )

    db.add(session)

    # -----------------------------------------------------
    # Create progress record if needed
    # -----------------------------------------------------

    progress = (
        db.query(Progress)
        .filter(
            Progress.user_id == current_user.id,
            Progress.topic_id == topic.id,
        )
        .first()
    )

    if not progress:
        progress = Progress(
            user_id=current_user.id,
            topic_id=topic.id,
            understanding_score=0.0,
            quiz_score=0.0,
            completion_percentage=0.0,
            status="in_progress",
            last_accessed=datetime.utcnow(),
        )

        db.add(progress)

    else:
        progress.status = "in_progress"
        progress.last_accessed = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "topic": topic.name,
        "video_id": video.youtube_id,
        "language": session.language,
        "progress": 0.0,
    }


# =========================================================
# LEARNING EVENT
# =========================================================

@router.post("/event")
async def learning_event(
    data: LearningEventRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    if data.event_type == "watch_time":
        if data.value is not None:
            session.watch_time_seconds = int(
                data.value
            )

    elif data.event_type == "progress":
        if data.value is not None:
            session.watch_percentage = max(
                0,
                min(
                    100,
                    data.value,
                ),
            )

    elif data.event_type == "completed":
        session.completed = True
        session.completed_at = datetime.utcnow()
        session.watch_percentage = 100

    db.commit()

    return {
        "session_id": session.id,
        "event_type": data.event_type,
        "value": data.value,
        "status": "recorded",
    }


# =========================================================
# UPDATE PROGRESS
# =========================================================

@router.patch("/progress/{session_id}")
async def update_learning_progress(
    session_id: int,
    data: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    percentage = data.progress * 100

    session.watch_percentage = percentage

    if session.topic_id:
        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == current_user.id,
                Progress.topic_id == session.topic_id,
            )
            .first()
        )

        if progress:
            progress.completion_percentage = percentage
            progress.last_accessed = datetime.utcnow()

            if percentage >= 100:
                progress.status = "completed"
            else:
                progress.status = "in_progress"

    db.commit()

    return {
        "session_id": session.id,
        "progress": data.progress,
        "status": "updated",
    }


# =========================================================
# COMPLETE
# =========================================================

@router.post("/complete/{session_id}")
async def complete_learning(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    session.watch_percentage = 100
    session.completed_at = datetime.utcnow()

    if session.topic_id:

        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == current_user.id,
                Progress.topic_id == session.topic_id,
            )
            .first()
        )

        if progress:
            progress.completion_percentage = 100
            progress.status = "completed"
            progress.last_accessed = datetime.utcnow()

    db.commit()

    return {
        "session_id": session.id,
        "completed": True,
    }


# =========================================================
# HISTORY
# =========================================================

@router.get("/history")
async def learning_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(LearningSession)
        .filter(
            LearningSession.user_id == current_user.id
        )
        .order_by(
            LearningSession.started_at.desc()
        )
        .all()
    )

    return {
        "sessions": [
            {
                "id": session.id,
                "video_id": session.video_id,
                "topic_id": session.topic_id,
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
                "language": session.language,
            }
            for session in sessions
        ],
    }