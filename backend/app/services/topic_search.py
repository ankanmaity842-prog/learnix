
import logging
from typing import Any

from app.ai.knowledge_graph import knowledge_graph
from app.ai.topic_classifier import topic_classifier
from app.services.youtube_service import youtube_service
from app.services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)


class TopicSearchService:

    async def analyze_topic(
        self,
        query: str,
        language: str = "en",
        level: str = "beginner",
    ) -> dict[str, Any]:

        query = query.strip()

        if not query:
            raise ValueError("Search query cannot be empty")

        if language not in {"en", "hi", "bn"}:
            raise ValueError("Unsupported language")

        if level not in {"beginner", "intermediate", "advanced"}:
            raise ValueError("Unsupported difficulty level")

        topic_info = await topic_classifier.classify(
            text=query,
            language=language,
            level=level,
        )

        topic = str(topic_info.get("topic") or query).strip()

        knowledge_graph.add_topic(
            topic=topic,
            prerequisites=topic_info.get("prerequisites", []),
            subtopics=topic_info.get("subtopics", []),
            related_topics=topic_info.get("related_topics", []),
        )

        return {
            "query": query,
            "topic": topic,
            "domain": topic_info.get("domain", "General"),
            "subtopics": topic_info.get("subtopics", []),
            "prerequisites": topic_info.get("prerequisites", []),
            "related_topics": topic_info.get("related_topics", []),
            "difficulty": level,
            "search_queries": topic_info.get("search_queries", []),
            "learning_path": knowledge_graph.get_learning_path(topic),
        }

    async def search(
        self,
        query: str,
        language: str = "en",
        level: str = "beginner",
        limit: int = 20,
    ) -> dict[str, Any]:

        if limit < 1:
            raise ValueError("limit must be at least 1")

        topic_info = await self.analyze_topic(
            query=query,
            language=language,
            level=level,
        )

        topic = topic_info["topic"]

        level_terms = {
            "beginner": "beginner basics for absolute beginners",
            "intermediate": "intermediate practical tutorial",
            "advanced": "advanced concepts deep dive",
        }

        # Search the topic itself first, then try a level-specific query.
        search_queries = [
            topic,
            f"{topic} {level_terms[level]} tutorial",
        ]

        videos_by_id = {}

        for search_query in search_queries:
            remaining = min(limit, 50) - len(videos_by_id)

            if remaining <= 0:
                break

            try:
                results = await youtube_service.search_videos(
                    query=search_query,
                    language=language,
                    limit=max(remaining, 5),
                    max_pages=1,
                    educational_only=True,
                    level=level,
                )

                videos = await youtube_service.enrich_search_results(
                    results
                )

                for video in videos:
                    video_id = video.get("video_id") or video.get("id")

                    # Deduplicate only when an ID is available.
                    if video_id:
                        videos_by_id[str(video_id)] = video

            except Exception:
                logger.exception(
                    "YouTube search failed for query=%r",
                    search_query,
                )

        candidates = list(videos_by_id.values())

        logger.info(
            "Topic search %r: fetched %d unique videos",
            topic,
            len(candidates),
        )

        relevant_videos = []

        for video in candidates:
            text = " ".join([
                str(video.get("title", "")),
                str(video.get("description", "")),
            ])

            if youtube_service.is_entertainment(text):
                continue

            relevance = recommendation_service._topic_relevance(
                video,
                topic,
            )

            if relevance < 0.20:
                continue

            video["language"] = language
            relevant_videos.append(video)

        logger.info(
            "Topic search %r: %d videos passed relevance filtering",
            topic,
            len(relevant_videos),
        )

        ranked = recommendation_service.rank_videos(
            videos=relevant_videos,
            topic=topic,
            learner_level=level,
            preferred_language=language,
        )

        selected = recommendation_service.select_level_videos(
            videos=ranked,
            level=level,
            limit=limit,
        )

        # Fallback: do not return an empty list solely because the
        # strict level selector rejected all otherwise relevant videos.
        if not selected and ranked:
            selected = ranked[:limit]

        return {
            **topic_info,
            "difficulty": level,
            "videos": selected,
            "returned_count": len(selected),
        }


topic_search_service = TopicSearchService()

