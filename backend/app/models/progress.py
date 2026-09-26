from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Progress(Base):
    __tablename__ = "progress"

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

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        index=True,
    )

    understanding_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    quiz_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    completion_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="not_started",
        nullable=False,
    )

    last_accessed: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="progress_records",
    )

    topic = relationship("Topic")