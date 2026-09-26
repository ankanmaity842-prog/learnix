from typing import Any

from app.ai.knowledge_graph import knowledge_graph
from app.ai.topic_classifier import topic_classifier
from app.services.youtube_service import youtube_service


class TopicSearchService:
    async def analyze_topic(
        self,
        query: str,
        language: str = "en",
    ) -> dict[str, Any]:
        query = query.strip()

        if not query:
            raise ValueError("Search query cannot be empty")

        topic_info = await topic_classifier.classify(
            text=query,
            language=language,
        )

        topic = topic_info.get("topic", query)
        domain = topic_info.get("domain", "General")
        subtopics = topic_info.get("subtopics", [])
        prerequisites = topic_info.get("prerequisites", [])
        related_topics = topic_info.get("related_topics", [])
        difficulty = topic_info.get(
            "difficulty",
            "intermediate",
        )
        search_queries = topic_info.get(
            "search_queries",
            [query],
        )

        knowledge_graph.add_topic(
            topic=topic,
            prerequisites=prerequisites,
            subtopics=subtopics,
            related_topics=related_topics,
        )

        learning_path = knowledge_graph.get_learning_path(topic)

        return {
            "query": query,
            "topic": topic,
            "domain": domain,
            "subtopics": subtopics,
            "prerequisites": prerequisites,
            "related_topics": related_topics,
            "difficulty": difficulty,
            "search_queries": search_queries,
            "learning_path": learning_path,
        }

    async def search(
        self,
        query: str,
        language: str = "en",
        limit: int = 10,
    ) -> dict[str, Any]:
        topic_info = await self.analyze_topic(
            query=query,
            language=language,
        )

        search_queries = topic_info["search_queries"]

        videos = []
        seen_video_ids = set()

        for search_query in search_queries[:3]:
            results = await youtube_service.search_videos(
                query=search_query,
                language=language,
                limit=limit,
            )

            for video in results:
                video_id = (
                    video.get("video_id")
                    or video.get("id")
                )

                if not video_id:
                    continue

                if video_id in seen_video_ids:
                    continue

                seen_video_ids.add(video_id)
                videos.append(video)

                if len(videos) >= limit:
                    break

            if len(videos) >= limit:
                break

        return {
            **topic_info,
            "videos": videos[:limit],
        }


topic_search_service = TopicSearchService()