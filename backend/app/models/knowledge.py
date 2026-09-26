from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Knowledge(Base):
    __tablename__ = "knowledge"

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

    mastery_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="unknown",
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    topic = relationship("Topic")


class KnowledgeRelationship(Base):
    __tablename__ = "knowledge_relationships"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
    )

    target_topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    strength: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    source_topic = relationship(
        "Topic",
        foreign_keys=[source_topic_id],
    )

    target_topic = relationship(
        "Topic",
        foreign_keys=[target_topic_id],
    )