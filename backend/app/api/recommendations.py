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

    limit: int | None = None


def get_level_limit(
    level: str,
    requested_limit: int | None,
) -> int:

    if level == "beginner":
        default = 45
        maximum = 50

    elif level == "intermediate":
        default = 25
        maximum = 30

    else:
        default = 12
        maximum = 15

    if requested_limit is None:
        return default

    return min(
        max(
            requested_limit,
            1,
        ),
        maximum,
    )


async def build_recommendations(
    topic: str,
    language: str,
    level: str,
    limit: int | None,
):

    final_limit = get_level_limit(
        level,
        limit,
    )

    topic_info = (
        await topic_classifier.classify(
            text=topic,
            language=language,
            level=level,
        )
    )

    resolved_topic = (
        topic_info.get("topic")
        or topic
    )

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

    level_terms = {
        "beginner": (
            "beginner basics "
            "from scratch fundamentals"
        ),
        "intermediate": (
            "intermediate practical "
            "projects implementation"
        ),
        "advanced": (
            "advanced deep dive "
            "internals architecture"
        ),
    }

    language_terms = {
        "en": (
            "English educational "
            "tutorial India"
        ),
        "hi": (
            "Hindi educational "
            "tutorial हिंदी"
        ),
        "bn": (
            "Bengali educational "
            "tutorial বাংলা"
        ),
    }

    queries = [
        (
            f"{resolved_topic} "
            f"{level_terms[level]} "
            f"{language_terms[language]}"
        )
    ]

    # Add classifier queries while preserving
    # the requested topic and level.
    for search_query in topic_info.get(
        "search_queries",
        [],
    ):

        if len(queries) >= 6:
            break

        query = (
            f"{resolved_topic} "
            f"{search_query} "
            f"{level_terms[level]} "
            f"{language_terms[language]}"
        )

        if query not in queries:
            queries.append(query)

    candidates = {}

    # We intentionally retrieve a large candidate
    # pool because the final level filtering happens
    # after YouTube metadata enrichment.
    for search_query in queries:

        results = (
            await youtube_service.search_videos(
                query=search_query,
                language=language,
                limit=50,
                max_pages=3,
                educational_only=True,
            )
        )

        for video in results:

            video_id = video.get(
                "video_id"
            )

            if not video_id:
                continue

            candidates[
                video_id
            ] = video

    videos = (
        await youtube_service.enrich_search_results(
            list(
                candidates.values()
            )
        )
    )

    # Strict educational filtering.
    videos = [
        video
        for video in videos
        if not youtube_service.is_entertainment(
            " ".join(
                [
                    str(
                        video.get(
                            "title",
                            "",
                        )
                    ),
                    str(
                        video.get(
                            "description",
                            "",
                        )
                    ),
                    str(
                        video.get(
                            "channel",
                            "",
                        )
                    ),
                ]
            )
        )
    ]

    # Hindi/Bengali language filtering.
    #
    # English remains open to global educational
    # creators, but Indian creators are ranked first.
    if language in {"hi", "bn"}:

        language_videos = [
            video
            for video in videos
            if video.get(
                "is_language_creator",
                False,
            )
        ]

        # If enough language-specific videos exist,
        # use them exclusively.
        if len(language_videos) >= final_limit:
            videos = language_videos
        else:
            # Preserve strict language preference
            # but don't return an empty page.
            videos = (
                language_videos
                + [
                    video
                    for video in videos
                    if video not in language_videos
                ]
            )

    ranked = (
        recommendation_service.rank_videos(
            videos=videos,
            topic=resolved_topic,
            learner_level=level,
            preferred_language=language,
        )
    )

    selected = (
        recommendation_service.select_level_videos(
            videos=ranked,
            level=level,
            limit=final_limit,
        )
    )

    return {
        "topic": resolved_topic,
        "domain": topic_info.get(
            "domain",
            "General",
        ),
        "language": language,
        "level": level,
        "requested_count": final_limit,
        "returned_count": len(selected),
        "difficulty": level,
        "prerequisites": topic_info.get(
            "prerequisites",
            [],
        ),
        "learning_path": (
            knowledge_graph.get_learning_path(
                resolved_topic
            )
        ),
        "recommendations": selected,
    }


@router.post("/")
async def get_recommendations(
    data: RecommendationRequest,
):

    return await build_recommendations(
        topic=data.topic.strip(),
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
    limit: int | None = Query(
        default=None,
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


@router.get("/channels")
async def recommended_channels(
    query: str = Query(
        ...,
        min_length=2,
    ),
    language: Literal[
        "en",
        "hi",
        "bn",
    ] = "en",
):

    channels = (
        await youtube_service.search_channels(
            query=query.strip(),
            language=language,
            limit=8,
        )
    )

    return {
        "query": query,
        "language": language,
        "channels": channels,
    }


@router.get("/next")
async def next_recommendation():

    return {
        "recommendation": None,
        "reason": (
            "No learning history available"
        ),
    }