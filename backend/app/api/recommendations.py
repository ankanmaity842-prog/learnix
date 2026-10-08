from typing import Literal

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from pydantic import BaseModel, Field

from app.ai.knowledge_graph import (
    knowledge_graph,
)
from app.ai.topic_classifier import (
    topic_classifier,
)
from app.services.youtube_service import (
    youtube_service,
)
from app.services.recommendation_service import (
    recommendation_service,
)


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


class RecommendationRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=2,
    )

    language: Literal[
        "en",
        "hi",
        "bn",
    ] = "en"

    level: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ] = "beginner"

    limit: int = Field(
        default=20,
        ge=1,
        le=30,
    )


LEVEL_TERMS = {
    "beginner": (
        "beginner basics "
        "from scratch tutorial"
    ),
    "intermediate": (
        "intermediate practical "
        "tutorial examples"
    ),
    "advanced": (
        "advanced concepts "
        "deep dive tutorial"
    ),
}


LANGUAGE_TERMS = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
}


async def build_recommendations(
    topic: str,
    language: str,
    level: str,
    limit: int,
):

    topic = topic.strip()

    topic_info = (
        await topic_classifier.classify(
            text=topic,
            language=language,
            level=level,
        )
    )

    # Preserve the user's exact search topic.
    resolved_topic = topic

    knowledge_graph.add_topic(
        topic=resolved_topic,
        prerequisites=topic_info.get(
            "prerequisites",
            [],
        ),
        subtopics=topic_info.get(
            "subtopics",
            [],
        ),
        related_topics=topic_info.get(
            "related_topics",
            [],
        ),
    )

    # IMPORTANT:
    # Do NOT use Gemini related search queries.
    # This prevents Python -> C++ / JavaScript etc.
    search_query = (
        f'"{resolved_topic}" '
        f'{LEVEL_TERMS[level]} '
        f'{LANGUAGE_TERMS[language]} '
        f'educational'
    )

    # Request many candidates so filtering does not leave
    # only a few videos.
    results = await youtube_service.search_videos(
        query=search_query,
        language=language,
        limit=50,
    )

    # Enrich with views, likes, duration and country.
    videos = (
        await youtube_service
        .enrich_search_results(
            results
        )
    )

    recommendations = (
        recommendation_service.rank_videos(
            videos=videos,
            topic=resolved_topic,
            learner_level=level,
            preferred_language=language,
        )
    )

    # Exactly the requested number, maximum 30.
    recommendations = recommendations[
        :limit
    ]

    return {
        "topic": resolved_topic,
        "domain": topic_info.get(
            "domain",
            "General",
        ),
        "language": language,
        "level": level,
        "difficulty": level,
        "prerequisites": topic_info.get(
            "prerequisites",
            [],
        ),
        "learning_path": (
            knowledge_graph
            .get_learning_path(
                resolved_topic
            )
        ),
        "count": len(
            recommendations
        ),
        "recommendations": recommendations,
    }


@router.post("/")
async def get_recommendations(
    data: RecommendationRequest,
):

    return await build_recommendations(
        topic=data.topic,
        language=data.language,
        level=data.level,
        limit=data.limit,
    )


@router.get(
    "/for-topic/{topic}"
)
async def recommendations_for_topic(
    topic: str,

    language: Literal[
        "en",
        "hi",
        "bn",
    ] = "en",

    level: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ] = "beginner",

    limit: int = Query(
        default=20,
        ge=1,
        le=30,
    ),
):

    if not topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    return await build_recommendations(
        topic=topic.strip(),
        language=language,
        level=level,
        limit=limit,
    )


@router.get("/next")
async def next_recommendation():

    return {
        "recommendation": None,
        "reason": (
            "No learning history available"
        ),
    }