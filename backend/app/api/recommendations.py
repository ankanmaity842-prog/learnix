
import logging
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ai.knowledge_graph import knowledge_graph
from app.ai.topic_classifier import topic_classifier
from app.services.youtube_service import youtube_service
from app.services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)

Language = Literal["en", "hi", "bn"]
Level = Literal["beginner", "intermediate", "advanced"]


class RecommendationRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    language: Language = "en"
    level: Level = "beginner"
    limit: int | None = Field(default=None, ge=1, le=50)


def get_level_limit(
    level: str,
    requested_limit: int | None,
) -> int:
    ranges = {
        "beginner": (30, 1, 30),
        "intermediate": (25, 1, 30),
        "advanced": (12, 1, 15),
    }

    default, minimum, maximum = ranges[level]

    if requested_limit is None:
        return default

    return max(minimum, min(requested_limit, maximum))


def _script_matches(video: dict, language: str) -> bool:
    """Detect script presence; not a reliable speech-language detector."""
    text = " ".join([
        str(video.get("title", "")),
        str(video.get("description", "")),
    ])

    if language == "hi":
        return bool(re.search(r"[\u0900-\u097F]", text))

    if language == "bn":
        return bool(re.search(r"[\u0980-\u09FF]", text))

    return True


def _safe_learning_path(topic: str) -> list:
    try:
        result = knowledge_graph.get_learning_path(topic)
        return result if isinstance(result, list) else []
    except Exception:
        logger.exception(
            "Could not create learning path for %r",
            topic,
        )
        return []


def _empty_response(
    topic: str,
    language: str,
    level: str,
    final_limit: int,
    topic_info: dict,
    channel_id: str | None,
    quota_exhausted: bool,
) -> dict:
    if quota_exhausted:
        message = (
            "YouTube search quota has been exhausted. "
            "Please try again after the quota resets. "
            "Previously cached results may still be available "
            "for other topics."
        )
    else:
        message = (
            "No usable videos were found for this topic. "
            "Try another topic or try again later."
        )

    return {
        "topic": topic,
        "domain": topic_info.get("domain", "General"),
        "language": language,
        "level": level,
        "requested_count": final_limit,
        "returned_count": 0,
        "difficulty": level,
        "prerequisites": topic_info.get("prerequisites", []),
        "learning_path": _safe_learning_path(topic),
        "channel_id": channel_id,
        "recommendations": [],
        "message": message,
        "error_code": (
            "YOUTUBE_SEARCH_QUOTA_EXCEEDED"
            if quota_exhausted
            else "NO_RECOMMENDATIONS_FOUND"
        ),
    }


async def build_recommendations(
    topic: str,
    language: str,
    level: str,
    limit: int | None,
    channel_id: str | None = None,
):
    topic = str(topic or "").strip()
    channel_id = str(channel_id or "").strip() or None

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty",
        )

    final_limit = get_level_limit(level, limit)

    logger.info(
        "Building recommendations: topic=%r language=%s "
        "level=%s limit=%d channel_filter=%s",
        topic,
        language,
        level,
        final_limit,
        channel_id or "none",
    )

    try:
        topic_info = await topic_classifier.classify(
            text=topic,
            language=language,
            level=level,
        )
        if not isinstance(topic_info, dict):
            topic_info = {}
    except Exception:
        logger.exception("Topic classification failed for %r", topic)
        topic_info = {}

    resolved_topic = (
        str(topic_info.get("topic") or topic).strip() or topic
    )

    try:
        knowledge_graph.add_topic(
            topic=resolved_topic,
            prerequisites=topic_info.get("prerequisites", []),
            subtopics=topic_info.get("subtopics", []),
            related_topics=topic_info.get("related_topics", []),
        )
    except Exception:
        logger.exception(
            "Knowledge graph update failed for topic %r",
            resolved_topic,
        )

    level_terms = {
        "beginner": "beginner basics fundamentals from scratch",
        "intermediate": "intermediate practical examples projects",
        "advanced": "advanced deep dive architecture optimization",
    }

    language_terms = {
        "en": "English",
        "hi": "Hindi हिंदी",
        "bn": "Bengali বাংলা",
    }

    # A cached result for the same query is reused by YouTubeService.
    # Keep the initial query broad to avoid spending quota unnecessarily.
    queries = [f"{resolved_topic} tutorial"]

    candidates: dict[str, dict] = {}

    def add_candidates(results: list[dict] | None) -> None:
        for video in results or []:
            video_id = str(
                video.get("video_id") or video.get("id") or ""
            ).strip()

            if not video_id:
                continue

            result_channel_id = str(
                video.get("channel_id") or ""
            ).strip()

            if channel_id and result_channel_id != channel_id:
                continue

            candidates[video_id] = {
                **video,
                "video_id": video_id,
                "channel_id": result_channel_id,
            }

    for search_query in queries:
        try:
            results = await youtube_service.search_videos(
                query=search_query,
                language=language,
                limit=50,
                max_pages=1,
                educational_only=True,
                channel_id=channel_id,
                level=level,
            )
        except Exception:
            logger.exception(
                "YouTube search raised an exception for query=%r",
                search_query,
            )
            continue

        logger.info(
            "Recommendation query completed: query=%r results=%d",
            search_query,
            len(results or []),
        )
        add_candidates(results)

    # Run one fallback search only when the first search did not return
    # enough candidates. Never run it if quota exhaustion is detected.
    if (
        len(candidates) < final_limit
        and not youtube_service.is_search_quota_exhausted()
    ):
        fallback_query = (
            f"{resolved_topic} {level_terms[level]} "
            f"{language_terms[language]}"
        )

        if fallback_query.casefold() not in {
            query.casefold() for query in queries
        }:
            try:
                fallback_results = await youtube_service.search_videos(
                    query=fallback_query,
                    language=language,
                    limit=50,
                    max_pages=1,
                    educational_only=True,
                    channel_id=channel_id,
                    level=level,
                )
                logger.info(
                    "Recommendation fallback completed: "
                    "query=%r results=%d",
                    fallback_query,
                    len(fallback_results or []),
                )
                add_candidates(fallback_results)
            except Exception:
                logger.exception(
                    "YouTube fallback search failed: query=%r",
                    fallback_query,
                )

    logger.info(
        "Recommendation candidates: topic=%r channel_filter=%s count=%d",
        resolved_topic,
        channel_id or "none",
        len(candidates),
    )

    if not candidates:
        return _empty_response(
            topic=resolved_topic,
            language=language,
            level=level,
            final_limit=final_limit,
            topic_info=topic_info,
            channel_id=channel_id,
            quota_exhausted=(
                youtube_service.is_search_quota_exhausted()
            ),
        )

    try:
        enriched = await youtube_service.enrich_search_results(
            list(candidates.values())
        )
        videos = enriched or list(candidates.values())
    except Exception:
        logger.exception("YouTube result enrichment failed")
        videos = list(candidates.values())

    filtered = []

    for video in videos:
        video_id = str(
            video.get("video_id") or video.get("id") or ""
        ).strip()

        if not video_id:
            continue

        result_channel_id = str(
            video.get("channel_id") or ""
        ).strip()

        if channel_id and result_channel_id != channel_id:
            continue

        video["video_id"] = video_id
        video["channel_id"] = result_channel_id
        video["language"] = language
        filtered.append(video)

    logger.info(
        "Recommendation post-enrichment: candidates=%d usable=%d "
        "channel_filter=%s",
        len(candidates),
        len(filtered),
        channel_id or "none",
    )

    try:
        ranked = recommendation_service.rank_videos(
            videos=filtered,
            topic=resolved_topic,
            learner_level=level,
            preferred_language=language,
        )
        ranked = ranked or []
    except Exception:
        logger.exception("Recommendation ranking failed")
        ranked = []

    # Preserve usable search results if ranking rejects all candidates.
    if not ranked:
        logger.warning(
            "Ranking returned no results for %r; using search candidates",
            resolved_topic,
        )
        ranked = filtered

    try:
        selected = recommendation_service.select_level_videos(
            videos=ranked,
            level=level,
            limit=final_limit,
        )
        selected = selected or []
    except Exception:
        logger.exception("Recommendation selection failed")
        selected = ranked[:final_limit]

    # Do not return zero if usable videos remain available.
    if not selected and ranked:
        logger.warning(
            "Level selection returned zero results; using ranked fallback"
        )
        selected = ranked[:final_limit]

    logger.info(
        "Recommendation completed: topic=%r candidates=%d "
        "enriched=%d ranked=%d selected=%d",
        resolved_topic,
        len(candidates),
        len(filtered),
        len(ranked),
        len(selected),
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
        "learning_path": _safe_learning_path(resolved_topic),
        "channel_id": channel_id,
        "recommendations": selected,
        "message": (
            "Some recommendations may be unavailable."
            if len(selected) < final_limit
            else None
        ),
    }


@router.post("/")
async def get_recommendations(data: RecommendationRequest):
    return await build_recommendations(
        topic=data.topic,
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
    return await build_recommendations(
        topic=topic,
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
        "returned_count": len(channels),
        "channels": channels,
        "message": (
            "YouTube search quota has been exhausted."
            if (
                not channels
                and youtube_service.is_search_quota_exhausted()
            )
            else None
        ),
    }


@router.get("/channel/{channel_id}")
async def recommendations_for_channel(
    channel_id: str,
    topic: str = Query(..., min_length=2),
    language: Language = "en",
    level: Level = "beginner",
    limit: int | None = Query(default=None, ge=1, le=50),
):
    channel_id = channel_id.strip()

    if not channel_id:
        raise HTTPException(
            status_code=400,
            detail="Channel ID is required",
        )

    return await build_recommendations(
        topic=topic,
        language=language,
        level=level,
        limit=limit,
        channel_id=channel_id,
    )


@router.get("/next")
async def next_recommendation():
    return {
        "recommendation": None,
        "reason": "No learning history available",
    }




