from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.knowledge_graph import knowledge_graph
from app.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.knowledge import Knowledge
from app.services.knowledge_gap_service import (
    knowledge_gap_service,
)
from app.services.learning_path_service import (
    learning_path_service,
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


class KnowledgeUpdate(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
    )

    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    source: str = "quiz"


def get_learner_knowledge(
    user_id: int,
    db: Session,
) -> dict[str, float]:

    records = (
        db.query(Knowledge)
        .join(Topic)
        .filter(
            Knowledge.user_id == user_id
        )
        .all()
    )

    return {
        record.topic.name: record.mastery_score
        for record in records
        if record.topic
    }


# =========================================================
# KNOWLEDGE MAP
# =========================================================

@router.get("/map")
async def get_knowledge_map(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    learner_knowledge = get_learner_knowledge(
        current_user.id,
        db,
    )

    return knowledge_graph.build_map(
        learner_knowledge
    )


# =========================================================
# KNOWLEDGE GAPS
# =========================================================

@router.get("/gaps")
async def get_knowledge_gaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    learner_knowledge = get_learner_knowledge(
        current_user.id,
        db,
    )

    gaps = []

    for topic in learner_knowledge:

        result = knowledge_gap_service.detect(
            target_topic=topic,
            learner_knowledge=learner_knowledge,
        )

        if not result["ready"]:
            gaps.append(
                {
                    "topic": topic,
                    "readiness_score": result[
                        "readiness_score"
                    ],
                    "missing_topics": result[
                        "missing_topics"
                    ],
                }
            )

    return {
        "knowledge_gaps": gaps,
    }


# =========================================================
# UPDATE KNOWLEDGE
# =========================================================

@router.post("/update")
async def update_knowledge(
    data: KnowledgeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic_name = data.topic.strip()

    if not topic_name:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

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

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.user_id == current_user.id,
            Knowledge.topic_id == topic.id,
        )
        .first()
    )

    if not knowledge:
        knowledge = Knowledge(
            user_id=current_user.id,
            topic_id=topic.id,
            mastery_score=data.score,
            confidence_score=data.score,
            status=(
                "strong"
                if data.score >= 0.8
                else "review"
                if data.score >= 0.5
                else "learning"
            ),
        )

        db.add(knowledge)

    else:
        knowledge.mastery_score = data.score
        knowledge.confidence_score = data.score

        if data.score >= 0.8:
            knowledge.status = "strong"
        elif data.score >= 0.5:
            knowledge.status = "review"
        else:
            knowledge.status = "learning"

    db.commit()
    db.refresh(knowledge)

    return {
        "topic": topic.name,
        "score": knowledge.mastery_score,
        "source": data.source,
        "status": knowledge.status,
    }


# =========================================================
# PREREQUISITES
# =========================================================

@router.get("/prerequisites/{topic}")
async def get_prerequisites(
    topic: str,
    current_user: User = Depends(get_current_user),
):
    topic = topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    return {
        "topic": topic,
        "prerequisites": (
            knowledge_graph.get_prerequisites(topic)
        ),
        "related_topics": (
            knowledge_graph.get_related_topics(topic)
        ),
        "subtopics": (
            knowledge_graph.get_subtopics(topic)
        ),
    }


# =========================================================
# READINESS
# =========================================================

@router.get("/readiness/{topic}")
async def check_topic_readiness(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic = topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    learner_knowledge = get_learner_knowledge(
        current_user.id,
        db,
    )

    result = knowledge_gap_service.detect(
        target_topic=topic,
        learner_knowledge=learner_knowledge,
    )

    path = learning_path_service.build_path(
        target_topic=topic,
        missing_topics=result["missing_topics"],
        learner_level="beginner",
    )

    return {
        "topic": topic,
        "ready": result["ready"],
        "readiness_score": result[
            "readiness_score"
        ],
        "missing_prerequisites": result[
            "missing_topics"
        ],
        "recommended_path": path["path"],
    }