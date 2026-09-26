from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    youtube_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    channel_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    difficulty_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    difficulty_level: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    visual_complexity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    visual_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    learning_sessions = relationship(
        "LearningSession",
        back_populates="video",
    )