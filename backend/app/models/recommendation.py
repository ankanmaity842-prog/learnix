from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

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
    )

    relevance_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    personalization_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    difficulty_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    visual_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    final_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="recommendations",
    )

    video = relationship(
        "Video",
        back_populates="recommendations",
    )

    topic = relationship("Topic")