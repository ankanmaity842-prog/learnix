from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.ai.knowledge_graph import knowledge_graph
from app.dependencies import get_current_user
from app.models.user import User
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
    topic: str = Field(..., min_length=2)
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )
    source: str = "quiz"


learner_knowledge: dict[str, float] = {}


@router.get("/map")
async def get_knowledge_map(
    current_user: User = Depends(get_current_user),
):
    return knowledge_graph.build_map(
        learner_knowledge
    )


@router.get("/gaps")
async def get_knowledge_gaps(
    current_user: User = Depends(get_current_user),
):
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


@router.post("/update")
async def update_knowledge(
    data: KnowledgeUpdate,
    current_user: User = Depends(get_current_user),
):
    topic = data.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    learner_knowledge[topic] = data.score

    return {
        "topic": topic,
        "score": data.score,
        "source": data.source,
        "status": "updated",
    }


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
        "prerequisites": knowledge_graph.get_prerequisites(
            topic
        ),
        "related_topics": knowledge_graph.get_related_topics(
            topic
        ),
        "subtopics": knowledge_graph.get_subtopics(
            topic
        ),
    }


@router.get("/readiness/{topic}")
async def check_topic_readiness(
    topic: str,
    current_user: User = Depends(get_current_user),
):
    topic = topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
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