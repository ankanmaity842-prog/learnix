from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.knowledge import Knowledge
from app.models.learning_session import LearningSession
from app.models.recommendation import Recommendation
from app.models.topic import Topic
from app.models.user import User
from app.models.video import Video


def get_user_by_id(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    preferred_language: str = "en",
):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        preferred_language=preferred_language,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_video_by_youtube_id(
    db: Session,
    youtube_id: str,
):
    return (
        db.query(Video)
        .filter(Video.youtube_id == youtube_id)
        .first()
    )


def create_video(
    db: Session,
    youtube_id: str,
    title: str,
    url: str,
    description: str | None = None,
    channel_name: str | None = None,
    duration_seconds: int | None = None,
):
    video = Video(
        youtube_id=youtube_id,
        title=title,
        description=description,
        channel_name=channel_name,
        url=url,
        duration_seconds=duration_seconds,
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    return video


def get_or_create_topic(
    db: Session,
    name: str,
    description: str | None = None,
    domain: str | None = None,
):
    topic = (
        db.query(Topic)
        .filter(Topic.name == name)
        .first()
    )

    if topic:
        return topic

    topic = Topic(
        name=name,
        description=description,
        domain=domain,
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return topic


def get_knowledge(
    db: Session,
    user_id: int,
    topic_id: int,
):
    return (
        db.query(Knowledge)
        .filter(
            Knowledge.user_id == user_id,
            Knowledge.topic_id == topic_id,
        )
        .first()
    )


def update_knowledge(
    db: Session,
    user_id: int,
    topic_id: int,
    mastery_score: float,
    confidence_score: float,
    status: str,
):
    knowledge = get_knowledge(
        db,
        user_id,
        topic_id,
    )

    if knowledge is None:
        knowledge = Knowledge(
            user_id=user_id,
            topic_id=topic_id,
        )
        db.add(knowledge)

    knowledge.mastery_score = mastery_score
    knowledge.confidence_score = confidence_score
    knowledge.status = status
    knowledge.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(knowledge)

    return knowledge


def create_learning_session(
    db: Session,
    user_id: int,
    video_id: int,
    topic_id: int | None = None,
    language: str = "en",
):
    session = LearningSession(
        user_id=user_id,
        video_id=video_id,
        topic_id=topic_id,
        language=language,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def update_learning_session(
    db: Session,
    session_id: int,
    watch_percentage: float | None = None,
    watch_time_seconds: int | None = None,
    quiz_score: float | None = None,
    completed: bool | None = None,
):
    session = (
        db.query(LearningSession)
        .filter(LearningSession.id == session_id)
        .first()
    )

    if session is None:
        return None

    if watch_percentage is not None:
        session.watch_percentage = watch_percentage

    if watch_time_seconds is not None:
        session.watch_time_seconds = watch_time_seconds

    if quiz_score is not None:
        session.quiz_score = quiz_score

    if completed is not None:
        session.completed = completed

        if completed:
            session.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return session


def create_recommendation(
    db: Session,
    user_id: int,
    video_id: int,
    topic_id: int | None,
    relevance_score: float,
    personalization_score: float,
    difficulty_score: float,
    visual_score: float,
    final_score: float,
    reason: str | None = None,
):
    recommendation = Recommendation(
        user_id=user_id,
        video_id=video_id,
        topic_id=topic_id,
        relevance_score=relevance_score,
        personalization_score=personalization_score,
        difficulty_score=difficulty_score,
        visual_score=visual_score,
        final_score=final_score,
        reason=reason,
    )

    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    return recommendation