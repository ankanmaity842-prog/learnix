import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ai.knowledge_graph import knowledge_graph
from app.ai.topic_classifier import topic_classifier
from app.services.youtube_service import youtube_service
from app.services.recommendation_service import recommendation_service


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)

Language = Literal["en", "hi", "bn"]
Level = Literal["beginner", "intermediate", "advanced"]


class RecommendationRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    language: Language = "en"
    level: Level = "beginner"
    limit: int | None = None


def get_level_limit(level: str, requested_limit: int | None) -> int:
    ranges = {
        "beginner": (30, 30, 30),
        "intermediate": (25, 20, 30),
        "advanced": (12, 10, 15),
    }
    default, minimum, maximum = ranges[level]

    if requested_limit is None:
        return default

    return max(minimum, min(requested_limit, maximum))


def _script_matches(video: dict, language: str) -> bool:
    """
    Conservative title/description script filter.
    This is NOT proof of spoken language; transcript verification
    is needed for a true spoken-language guarantee.
    """
    if language == "en":
        return True

    text = " ".join([
        str(video.get("title", "")),
        str(video.get("description", "")),
    ])

    if language == "hi":
        return bool(re.search(r"[\u0900-\u097F]", text))

    if language == "bn":
        return bool(re.search(r"[\u0980-\u09FF]", text))

    return False


async def build_recommendations(
    topic: str,
    language: str,
    level: str,
    limit: int | None,
    channel_id: str | None = None,
):
    final_limit = get_level_limit(level, limit)

    topic_info = await topic_classifier.classify(
        text=topic,
        language=language,
        level=level,
    )
    resolved_topic = topic_info.get("topic") or topic

    knowledge_graph.add_topic(
        topic=resolved_topic,
        prerequisites=topic_info.get("prerequisites", []),
        subtopics=topic_info.get("subtopics", []),
        related_topics=topic_info.get("related_topics", []),
    )

    level_terms = {
        "beginner": "beginner basics fundamentals from scratch",
        "intermediate": "intermediate practical examples projects",
        "advanced": "advanced deep dive architecture optimization",
    }
    language_terms = {
        "en": "English educational tutorial",
        "hi": "Hindi हिंदी शैक्षिक ट्यूटोरियल",
        "bn": "Bengali বাংলা শিক্ষামূলক টিউটোরিয়াল",
    }

    base_query = (
        f"{resolved_topic} "
        f"{level_terms[level]} "
        f"{language_terms[language]}"
    )

    # Keep the search bounded to reduce YouTube API quota use.
    queries = [base_query]
    if not channel_id:
        for item in topic_info.get("search_queries", []):
            if len(queries) >= 3:
                break
            if item and item.strip():
                query = (
                    f"{resolved_topic} {item.strip()} "
                    f"{level_terms[level]} {language_terms[language]}"
                )
                if query not in queries:
                    queries.append(query)

    candidates = {}
    for search_query in queries:
        results = await youtube_service.search_videos(
            query=search_query,
            language=language,
            limit=50,
            max_pages=2,
            educational_only=True,
            channel_id=channel_id,
        )

        for video in results:
            video_id = video.get("video_id")
            if video_id:
                candidates[video_id] = video

    videos = await youtube_service.enrich_search_results(
        list(candidates.values())
    )

    filtered = []
    for video in videos:
        text = " ".join([
            str(video.get("title", "")),
            str(video.get("description", "")),
        ])

        if youtube_service.is_entertainment(text):
            continue

        # Avoid cross-topic spillover where the title/description
        # has no meaningful overlap with the requested topic.
        if recommendation_service._topic_relevance(
            video, resolved_topic
        ) < 0.20:
            continue

        # For Hindi/Bengali, conservatively reject results without
        # the corresponding script. This is a preliminary filter,
        # not a substitute for checking actual transcript language.
        if language in {"hi", "bn"} and not _script_matches(
            video, language
        ):
            continue

        video["language"] = language
        filtered.append(video)

    ranked = recommendation_service.rank_videos(
        videos=filtered,
        topic=resolved_topic,
        learner_level=level,
        preferred_language=language,
    )

    selected = recommendation_service.select_level_videos(
        videos=ranked,
        level=level,
        limit=final_limit,
    )

    return {
        "topic": resolved_topic,
        "domain": topic_info.get("domain", "General"),
        "language": language,
        "level": level,
        "requested_count": final_limit,
        "returned_count": len(selected),
        "difficulty": level,
        "prerequisites": topic_info.get("prerequisites", []),
        "learning_path": knowledge_graph.get_learning_path(
            resolved_topic
        ),
        "channel_id": channel_id,
        "recommendations": selected,
    }


@router.post("/")
async def get_recommendations(data: RecommendationRequest):
    if not data.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    return await build_recommendations(
        topic=data.topic.strip(),
        language=data.language,
        level=data.level,
        limit=data.limit,
    )


@router.get("/for-topic/{topic}")
async def recommendations_for_topic(
    topic: str,
    language: Language = "en",
    level: Level = "beginner",
    limit: int | None = Query(default=None, ge=1, le=50),
):
    if not topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    return await build_recommendations(
        topic=topic.strip(),
        language=language,
        level=level,
        limit=limit,
    )


@router.get("/channels")
async def recommended_channels(
    query: str = Query(..., min_length=2),
    language: Language = "en",
):
    channels = await youtube_service.search_channels(
        query=query.strip(),
        language=language,
        limit=8,
    )

    return {
        "query": query,
        "language": language,
        "channels": channels,
    }


@router.get("/channel/{channel_id}")
async def recommendations_for_channel(
    channel_id: str,
    topic: str = Query(..., min_length=2),
    language: Language = "en",
    level: Level = "beginner",
    limit: int | None = Query(default=None, ge=1, le=50),
):
    if not channel_id.strip():
        raise HTTPException(status_code=400, detail="Channel ID is required")

    return await build_recommendations(
        topic=topic.strip(),
        language=language,
        level=level,
        limit=limit,
        channel_id=channel_id.strip(),
    )


@router.get("/next")
async def next_recommendation():
    return {
        "recommendation": None,
        "reason": "No learning history available",
    }