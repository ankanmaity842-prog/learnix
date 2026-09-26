from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.youtube_service import youtube_service
from app.ai.topic_classifier import topic_classifier
from app.ai.knowledge_graph import knowledge_graph
from app.services.transcript_service import transcript_service
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def search_topics(
    q: str = Query(..., min_length=2),
    language: str = "en",
    level: str = "beginner",
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Search educational content using the dynamic learning pipeline.

    Flow:
        Query
          ↓
        Language
          ↓
        Topic understanding
          ↓
        Prerequisites / Knowledge Graph
          ↓
        YouTube search
          ↓
        Transcript extraction
          ↓
        Video feature analysis
          ↓
        Personalized ranking
    """

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    if language not in {"en", "bn", "hi"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Use en, bn, or hi.",
        )

    try:
        topic_info = await topic_classifier.classify(
            text=query,
            language=language,
        )

        topic = topic_info["topic"]
        prerequisites = topic_info.get("prerequisites", [])
        subtopics = topic_info.get("subtopics", [])
        related_topics = topic_info.get("related_topics", [])

        knowledge_graph.add_topic(
            topic=topic,
            prerequisites=prerequisites,
            subtopics=subtopics,
            related_topics=related_topics,
        )

        search_queries = topic_info.get("search_queries", [query])

        videos = []

        for search_query in search_queries[:3]:
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

            if video_id and video_id not in unique_videos:
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
                "transcript_available": bool(transcript),
                "transcript": transcript,
            })

        recommendations = recommendation_service.rank_videos(
            videos=enriched_videos,
            topic=topic,
            learner_level=level,
        )

        return {
            "query": query,
            "language": language,
            "level": level,
            "topic": topic,
            "domain": topic_info.get("domain", "General"),
            "difficulty": topic_info.get(
                "difficulty",
                "intermediate",
            ),
            "subtopics": subtopics,
            "prerequisites": prerequisites,
            "related_topics": related_topics,
            "learning_path": knowledge_graph.get_learning_path(topic),
            "recommendations": recommendations,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Search pipeline failed: {str(exc)}",
        ) from exc