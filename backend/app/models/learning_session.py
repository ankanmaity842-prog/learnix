from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.connection import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id"),
        nullable=True,
        index=True,
    )

    watch_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    watch_time_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    quiz_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="learning_sessions",
    )

    video = relationship(
        "Video",
        back_populates="learning_sessions",
    )

    topic = relationship(
        "Topic",
    )