import asyncio
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ai.topic_classifier import topic_classifier
from app.ai.knowledge_graph import knowledge_graph
from app.services.youtube_service import youtube_service
from app.services.video_feature_service import video_feature_service
from app.services.recommendation_service import recommendation_service


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


class RecommendationRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    language: Literal["en", "bn", "hi"] = "en"
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    limit: int = Field(default=20, ge=1, le=20)


async def build_recommendations(
    topic: str,
    language: str,
    level: str,
    limit: int,
):
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
        "beginner": "beginner basics explained from scratch",
        "intermediate": "intermediate practical examples tutorial",
        "advanced": "advanced concepts deep dive",
    }
    language_terms = {
        "en": "English tutorial",
        "hi": "Hindi tutorial हिंदी में",
        "bn": "Bengali tutorial বাংলা ভাষায়",
    }

    queries = [
        f"{resolved_topic} {level_terms[level]} {language_terms[language]}"
    ]

    for search_query in topic_info.get("search_queries", []):
        if len(queries) >= 3:
            break
        localized_query = (
            f"{search_query} {level_terms[level]} "
            f"{language_terms[language]}"
        )
        if localized_query not in queries:
            queries.append(localized_query)

    candidates = {}
    for search_query in queries:
        results = await youtube_service.search_videos(
            query=search_query,
            language=language,
            limit=20,
        )
        for video in results:
            video_id = video.get("video_id")
            if video_id:
                candidates[video_id] = video

    videos = await youtube_service.enrich_search_results(
        list(candidates.values())
    )

    if language == "bn":
        semaphore = asyncio.Semaphore(5)

        async def inspect_thumbnail(video):
            async with semaphore:
                video["thumbnail_has_bengali"] = (
                    await video_feature_service.has_bengali_thumbnail_text(
                        video.get("thumbnail", "")
                    )
                )

        await asyncio.gather(
            *(inspect_thumbnail(video) for video in videos)
        )

    recommendations = recommendation_service.rank_videos(
        videos=videos,
        topic=resolved_topic,
        learner_level=level,
        preferred_language=language,
    )[:limit]

    return {
        "topic": resolved_topic,
        "domain": topic_info.get("domain", "General"),
        "language": language,
        "level": level,
        "difficulty": level,
        "prerequisites": topic_info.get("prerequisites", []),
        "learning_path": knowledge_graph.get_learning_path(resolved_topic),
        "recommendations": recommendations,
    }


@router.post("/")
async def get_recommendations(data: RecommendationRequest):
    return await build_recommendations(
        topic=data.topic.strip(),
        language=data.language,
        level=data.level,
        limit=data.limit,
    )


@router.get("/for-topic/{topic}")
async def recommendations_for_topic(
    topic: str,
    language: Literal["en", "bn", "hi"] = "en",
    level: Literal["beginner", "intermediate", "advanced"] = "beginner",
    limit: int = Query(20, ge=1, le=20),
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
        "reason": "No learning history available",
    }
