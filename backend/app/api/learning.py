from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload
from app.models.search_history import SearchHistory

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
    topic: str = Field(..., min_length=2)
    video_id: str | None = None
    language: str = "en"

    title: str | None = None
    description: str | None = None
    channel: str | None = None
    thumbnail: str | None = None


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

        if not data.video_id:
            raise HTTPException(
            status_code=400,
            detail="video_id is required",
        )

    video = (
        db.query(Video)
        .filter(Video.youtube_id == data.video_id)
        .first()
    )

    if not video:
        if not data.title:
            raise HTTPException(
                status_code=422,
                detail="Video title is required for a new video",
            )

        video = Video(
            youtube_id=data.video_id,
            title=data.title,
            description=data.description,
            channel_name=data.channel,
            url=f"https://www.youtube.com/watch?v={data.video_id}",
            thumbnail=data.thumbnail,
            language=data.language,
        )

        db.add(video)
        db.flush()
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

# =========================================================
# SAVE SEARCH HISTORY
# =========================================================

class SearchHistoryRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255)


@router.post("/search-history")
async def save_search_history(
    data: SearchHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic_name = data.topic.strip()

    if not topic_name:
        raise HTTPException(
            status_code=422,
            detail="Topic cannot be empty",
        )

    record = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.user_id == current_user.id,
            SearchHistory.topic.ilike(topic_name),
        )
        .first()
    )

    now = datetime.utcnow()

    if record:
        record.searched_at = now
        record.topic = topic_name
    else:
        record = SearchHistory(
            user_id=current_user.id,
            topic=topic_name,
            searched_at=now,
        )
        db.add(record)

    db.commit()

    return {
        "topic": record.topic,
        "searched_at": record.searched_at,
    }


# =========================================================
# EXPLORE HISTORY
# =========================================================

@router.get("/explore-history")
async def get_explore_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    searches = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.searched_at.desc())
        .limit(10)
        .all()
    )

    sessions = (
        db.query(LearningSession)
        .options(
            joinedload(LearningSession.video),
            joinedload(LearningSession.topic),
        )
        .filter(LearningSession.user_id == current_user.id)
        .order_by(LearningSession.started_at.desc())
        .limit(50)
        .all()
    )

    videos = []
    seen_video_ids = set()

    for session in sessions:
        video = session.video

        if not video or video.youtube_id in seen_video_ids:
            continue

        seen_video_ids.add(video.youtube_id)

        videos.append({
            "video_id": video.youtube_id,
            "title": video.title,
            "description": video.description or "",
            "channel": video.channel_name or "Educational channel",
            "thumbnail": video.thumbnail,
            "language": video.language,
            "topic": (
                session.topic.name
                if session.topic
                else "Previously watched"
            ),
            "watch_percentage": session.watch_percentage,
            "watch_time_seconds": session.watch_time_seconds,
            "started_at": session.started_at,
        })

        if len(videos) == 10:
            break

    return {
        "recent_searches": [
            {
                "topic": item.topic,
                "searched_at": item.searched_at,
            }
            for item in searches
        ],
        "recent_videos": videos,
    }
