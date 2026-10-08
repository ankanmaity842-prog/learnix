from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.progress import Progress
from app.models.learning_session import LearningSession
from app.models.knowledge import Knowledge
from app.models.topic import Topic


router = APIRouter(
    prefix="/progress",
    tags=["Progress"],
)


# =========================================================
# HELPERS
# =========================================================

def calculate_streak(sessions: list[LearningSession]) -> int:
    if not sessions:
        return 0

    dates = {
        session.started_at.date()
        for session in sessions
        if session.started_at
    }

    if not dates:
        return 0

    today = datetime.utcnow().date()

    # If the user hasn't learned today, allow yesterday
    # to be the beginning of the current streak.
    if today not in dates:
        today = today - timedelta(days=1)

        if today not in dates:
            return 0

    streak = 0
    current_date = today

    while current_date in dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def format_learning_time(seconds: int) -> str:
    hours = seconds / 3600

    if hours < 1:
        minutes = max(1, round(seconds / 60))
        return f"{minutes}m"

    return f"{hours:.1f}h"


# =========================================================
# OVERALL PROGRESS
# =========================================================

@router.get("/")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress_records = (
        db.query(Progress)
        .filter(
            Progress.user_id == current_user.id
        )
        .all()
    )

    sessions = (
        db.query(LearningSession)
        .filter(
            LearningSession.user_id == current_user.id
        )
        .all()
    )

    completed_topics = sum(
        1
        for record in progress_records
        if record.completion_percentage >= 100
    )

    completed_videos = sum(
        1
        for session in sessions
        if session.completed
    )

    quiz_scores = [
        session.quiz_score
        for session in sessions
        if session.quiz_score is not None
    ]

    average_quiz_score = (
        sum(quiz_scores) / len(quiz_scores)
        if quiz_scores
        else 0
    )

    overall_progress = (
        sum(
            record.completion_percentage
            for record in progress_records
        )
        / len(progress_records)
        if progress_records
        else 0
    )

    total_watch_time = sum(
        session.watch_time_seconds or 0
        for session in sessions
    )

    return {
        "overall_progress": round(
            overall_progress,
            1,
        ),
        "topics_completed": completed_topics,
        "videos_completed": completed_videos,
        "quizzes_completed": len(quiz_scores),
        "average_quiz_score": round(
            average_quiz_score,
            1,
        ),
        "learning_streak": calculate_streak(
            sessions
        ),
        "learning_sessions": len(sessions),
        "learning_time_seconds": total_watch_time,
        "learning_time": format_learning_time(
            total_watch_time
        ),
    }


# =========================================================
# TOPIC PROGRESS
# =========================================================

@router.get("/topics")
async def topic_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Progress)
        .options(joinedload(Progress.topic))
        .filter(
            Progress.user_id == current_user.id
        )
        .order_by(
            Progress.last_accessed.desc()
        )
        .all()
    )

    topics = []

    for record in records:
        topics.append(
            {
                "topic_id": record.topic_id,
                "topic": (
                    record.topic.name
                    if record.topic
                    else "Unknown topic"
                ),
                "understanding_score": (
                    record.understanding_score
                ),
                "quiz_score": record.quiz_score,
                "completion_percentage": (
                    record.completion_percentage
                ),
                "status": record.status,
                "last_accessed": (
                    record.last_accessed
                ),
            }
        )

    return {
        "topics": topics,
    }


# =========================================================
# WEEKLY LEARNING
# =========================================================

@router.get("/weekly")
async def weekly_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().date()

    start_date = today - timedelta(days=6)

    sessions = (
        db.query(LearningSession)
        .filter(
            LearningSession.user_id == current_user.id,
            LearningSession.started_at >= datetime.combine(
                start_date,
                datetime.min.time(),
            ),
        )
        .all()
    )

    days = []
    minutes = []
    session_counts = []

    for offset in range(7):
        current_date = start_date + timedelta(
            days=offset
        )

        day_sessions = [
            session
            for session in sessions
            if session.started_at.date()
            == current_date
        ]

        total_seconds = sum(
            session.watch_time_seconds or 0
            for session in day_sessions
        )

        days.append(
            current_date.strftime("%a")
        )

        minutes.append(
            round(total_seconds / 60)
        )

        session_counts.append(
            len(day_sessions)
        )

    return {
        "days": days,
        "minutes": minutes,
        "sessions": session_counts,
    }


# =========================================================
# DASHBOARD
# =========================================================

@router.get("/dashboard")
async def progress_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress_records = (
        db.query(Progress)
        .options(joinedload(Progress.topic))
        .filter(
            Progress.user_id == current_user.id
        )
        .order_by(
            Progress.last_accessed.desc()
        )
        .all()
    )

    sessions = (
        db.query(LearningSession)
        .options(
            joinedload(LearningSession.video),
            joinedload(LearningSession.topic),
        )
        .filter(
            LearningSession.user_id == current_user.id
        )
        .order_by(
            LearningSession.started_at.desc()
        )
        .all()
    )

    knowledge_records = (
        db.query(Knowledge)
        .filter(
            Knowledge.user_id == current_user.id
        )
        .all()
    )

    # -----------------------------------------------------
    # Progress
    # -----------------------------------------------------

    overall_progress = (
        sum(
            record.completion_percentage
            for record in progress_records
        )
        / len(progress_records)
        if progress_records
        else 0
    )

    understanding_scores = [
        record.understanding_score
        for record in progress_records
    ]

    quiz_scores = [
        session.quiz_score
        for session in sessions
        if session.quiz_score is not None
    ]

    understanding_score = (
        sum(understanding_scores)
        / len(understanding_scores)
        if understanding_scores
        else 0
    )

    quiz_accuracy = (
        sum(quiz_scores)
        / len(quiz_scores)
        if quiz_scores
        else 0
    )

    # -----------------------------------------------------
    # Knowledge
    # -----------------------------------------------------

    strong_count = sum(
        1
        for item in knowledge_records
        if item.status.lower()
        in {"strong", "mastered", "completed"}
        or item.mastery_score >= 0.8
    )

    review_count = sum(
        1
        for item in knowledge_records
        if item.status.lower()
        in {"review", "needs_review"}
        or (
            0.5
            <= item.mastery_score
            < 0.8
        )
    )

    learning_count = sum(
        1
        for item in knowledge_records
        if item.status.lower()
        in {
            "learning",
            "in_progress",
            "unknown",
        }
        or item.mastery_score < 0.5
    )

    # -----------------------------------------------------
    # Current learning
    # -----------------------------------------------------

    current_progress = next(
        (
            record
            for record in progress_records
            if record.completion_percentage < 100
        ),
        None,
    )

    current_learning = None

    if current_progress:
        current_learning = {
            "topic_id": current_progress.topic_id,
            "topic": (
                current_progress.topic.name
                if current_progress.topic
                else "Current topic"
            ),
            "progress": round(
                current_progress.completion_percentage,
                1,
            ),
            "understanding_score": (
                current_progress.understanding_score
            ),
            "last_accessed": (
                current_progress.last_accessed
            ),
        }

    # -----------------------------------------------------
    # Learning time
    # -----------------------------------------------------

    total_watch_time = sum(
        session.watch_time_seconds or 0
        for session in sessions
    )

    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    monthly_seconds = sum(
        session.watch_time_seconds or 0
        for session in sessions
        if session.started_at.month == current_month
        and session.started_at.year == current_year
    )

    # -----------------------------------------------------
    # Recent activity
    # -----------------------------------------------------

    recent_activity = []

    for session in sessions[:5]:

        topic_name = (
            session.topic.name
            if session.topic
            else "Learning session"
        )

        video_title = (
            session.video.title
            if session.video
            else None
        )

        if session.completed:
            activity_type = "completed"
            title = "Completed learning session"
            status = "Completed"

        elif session.watch_percentage > 0:
            activity_type = "progress"
            title = "Learning session in progress"
            status = "In progress"

        else:
            activity_type = "started"
            title = "Started learning session"
            status = "Started"

        recent_activity.append(
            {
                "type": activity_type,
                "title": title,
                "topic": topic_name,
                "video_title": video_title,
                "status": status,
                "progress": (
                    session.watch_percentage
                ),
                "created_at": session.started_at,
            }
        )

    # -----------------------------------------------------
    # Dashboard response
    # -----------------------------------------------------

    return {
        "stats": {
            "learning_sessions": len(sessions),
            "completed_lessons": sum(
                1
                for session in sessions
                if session.completed
            ),
            "learning_time": format_learning_time(
                monthly_seconds
            ),
            "learning_time_seconds": monthly_seconds,
            "current_streak": calculate_streak(
                sessions
            ),
        },

        "progress": {
            "overall_progress": round(
                overall_progress,
                1,
            ),
            "understanding_score": round(
                understanding_score,
                1,
            ),
            "quiz_accuracy": round(
                quiz_accuracy,
                1,
            ),
        },

        "current_learning": current_learning,

        "knowledge": {
            "strong": strong_count,
            "review": review_count,
            "learning": learning_count,
            "total": len(knowledge_records),
        },

        "recent_activity": recent_activity,
    }