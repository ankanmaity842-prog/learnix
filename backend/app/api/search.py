
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.youtube_service import youtube_service
from app.ai.topic_classifier import topic_classifier
from app.ai.knowledge_graph import knowledge_graph
from app.services.transcript_service import transcript_service
from app.services.recommendation_service import recommendation_service


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

VALID_LANGUAGES = {"en", "bn", "hi"}
VALID_LEVELS = {"beginner", "intermediate", "advanced"}


@router.get("/")
async def search_topics(
    q: str = Query(..., min_length=2),
    language: str = "en",
    level: str = "beginner",
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    if language not in VALID_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Use en, bn, or hi.",
        )

    if level not in VALID_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported level. Use beginner, "
                "intermediate, or advanced."
            ),
        )

    try:
        topic_info = await topic_classifier.classify(
            text=query,
            language=language,
            level=level,
        )

        topic = topic_info.get("topic") or query
        prerequisites = topic_info.get("prerequisites", [])
        subtopics = topic_info.get("subtopics", [])
        related_topics = topic_info.get("related_topics", [])

        knowledge_graph.add_topic(
            topic=topic,
            prerequisites=prerequisites,
            subtopics=subtopics,
            related_topics=related_topics,
        )

        search_queries = topic_info.get("search_queries") or [query]

        # Search a bounded number of queries to control API quota.
        unique_videos = {}

        for search_query in search_queries[:3]:
            results = await youtube_service.search_videos(
                query=search_query,
                language=language,
                limit=min(limit, 50),
                max_pages=1,
                educational_only=True,
                level=level,
            )

            for video in results:
                video_id = video.get("video_id") or video.get("id")

                if video_id:
                    unique_videos[video_id] = video

            if len(unique_videos) >= limit:
                break

        videos = list(unique_videos.values())

        # Retrieve full descriptions and metadata before filtering.
        videos = await youtube_service.enrich_search_results(videos)

        enriched_videos = []

        for video in videos:
            video_id = video.get("video_id") or video.get("id")

            if not video_id:
                continue

            text = " ".join(
                [
                    str(video.get("title", "")),
                    str(video.get("description", "")),
                ]
            )

            if youtube_service.is_entertainment(text):
                continue

            if recommendation_service._topic_relevance(
                video,
                topic,
            ) < 0.20:
                continue

            transcript = ""

            try:
                transcript = await transcript_service.get_transcript(
                    video_id
                )
            except Exception:
                transcript = ""

            enriched_videos.append(
                {
                    **video,
                    "video_id": video_id,
                    "transcript_available": bool(transcript),
                    "transcript": transcript,
                    "language": language,
                }
            )

        ranked = recommendation_service.rank_videos(
            videos=enriched_videos,
            topic=topic,
            learner_level=level,
            preferred_language=language,
        )

        recommendations = recommendation_service.select_level_videos(
            videos=ranked,
            level=level,
            limit=limit,
        )

        return {
            "query": query,
            "language": language,
            "level": level,
            "topic": topic,
            "domain": topic_info.get("domain", "General"),
            "difficulty": level,
            "subtopics": subtopics,
            "prerequisites": prerequisites,
            "related_topics": related_topics,
            "learning_path": knowledge_graph.get_learning_path(topic),
            "recommendations": recommendations,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Search pipeline failed: {str(exc)}",
        ) from exc
