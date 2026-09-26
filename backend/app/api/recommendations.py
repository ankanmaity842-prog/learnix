from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.ai.topic_classifier import topic_classifier
from app.ai.knowledge_graph import knowledge_graph
from app.services.youtube_service import youtube_service
from app.services.transcript_service import transcript_service
from app.services.recommendation_service import recommendation_service

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


class RecommendationRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    language: str = "en"
    level: str = "beginner"
    limit: int = Field(default=10, ge=1, le=50)


async def build_recommendations(
    topic: str,
    language: str,
    level: str,
    limit: int,
):
    topic_info = await topic_classifier.classify(
        text=topic,
        language=language,
    )

    resolved_topic = topic_info["topic"]

    knowledge_graph.add_topic(
        topic=resolved_topic,
        prerequisites=topic_info.get("prerequisites", []),
        subtopics=topic_info.get("subtopics", []),
        related_topics=topic_info.get("related_topics", []),
    )

    queries = topic_info.get(
        "search_queries",
        [topic],
    )

    videos = []

    for search_query in queries[:3]:
        results = await youtube_service.search_videos(
            query=search_query,
            language=language,
            limit=limit,
        )

        videos.extend(results)

        if len(videos) >= limit:
            break

    unique_videos = {}

    for video in videos:
        video_id = video.get("video_id") or video.get("id")

        if video_id:
            unique_videos[video_id] = video

    videos = list(unique_videos.values())[:limit]

    enriched_videos = []

    for video in videos:
        video_id = video.get("video_id") or video.get("id")

        transcript = ""

        try:
            transcript = await transcript_service.get_transcript(
                video_id
            )
        except Exception:
            transcript = ""

        enriched_videos.append({
            **video,
            "transcript": transcript,
            "transcript_available": bool(transcript),
        })

    recommendations = recommendation_service.rank_videos(
        videos=enriched_videos,
        topic=resolved_topic,
        learner_level=level,
    )

    return {
        "topic": resolved_topic,
        "domain": topic_info.get("domain", "General"),
        "language": language,
        "level": level,
        "difficulty": topic_info.get(
            "difficulty",
            "intermediate",
        ),
        "prerequisites": topic_info.get(
            "prerequisites",
            [],
        ),
        "learning_path": knowledge_graph.get_learning_path(
            resolved_topic
        ),
        "recommendations": recommendations,
    }


@router.post("/")
async def get_recommendations(
    data: RecommendationRequest,
):
    """
    Generate personalized recommendations.
    """

    if data.language not in {"en", "bn", "hi"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Use en, bn, or hi.",
        )

    return await build_recommendations(
        topic=data.topic.strip(),
        language=data.language,
        level=data.level,
        limit=data.limit,
    )


@router.get("/for-topic/{topic}")
async def recommendations_for_topic(
    topic: str,
    language: str = "en",
    level: str = "beginner",
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get recommendations for a specific educational topic.
    """

    if not topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    if language not in {"en", "bn", "hi"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Use en, bn, or hi.",
        )

    return await build_recommendations(
        topic=topic.strip(),
        language=language,
        level=level,
        limit=limit,
    )


@router.get("/next")
async def next_recommendation():
    """
    Recommend the next learning resource.

    This endpoint will be connected to learner history,
    knowledge state, and adaptive learning path logic.
    """

    return {
        "recommendation": None,
        "reason": "No learning history available",
    }