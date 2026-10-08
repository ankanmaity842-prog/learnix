from typing import Any

from app.ai.knowledge_graph import (
    knowledge_graph,
)
from app.ai.topic_classifier import (
    topic_classifier,
)
from app.services.youtube_service import (
    youtube_service,
)


class TopicSearchService:

    async def analyze_topic(
        self,
        query: str,
        language: str = "en",
        level: str = "beginner",
    ) -> dict[str, Any]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty"
            )

        topic_info = (
            await topic_classifier.classify(
                text=query,
                language=language,
                level=level,
            )
        )

        topic = query

        knowledge_graph.add_topic(
            topic=topic,
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

        return {
            "query": query,
            "topic": topic,
            "domain": topic_info.get(
                "domain",
                "General",
            ),
            "subtopics": topic_info.get(
                "subtopics",
                [],
            ),
            "prerequisites": topic_info.get(
                "prerequisites",
                [],
            ),
            "related_topics": topic_info.get(
                "related_topics",
                [],
            ),
            "difficulty": level,
            "search_queries": [],
            "learning_path": (
                knowledge_graph
                .get_learning_path(topic)
            ),
        }

    async def search(
        self,
        query: str,
        language: str = "en",
        level: str = "beginner",
        limit: int = 20,
    ) -> dict[str, Any]:

        topic_info = (
            await self.analyze_topic(
                query=query,
                language=language,
                level=level,
            )
        )

        topic = topic_info["topic"]

        level_terms = {
            "beginner": (
                "beginner basics "
                "from scratch tutorial"
            ),
            "intermediate": (
                "intermediate practical tutorial"
            ),
            "advanced": (
                "advanced deep dive tutorial"
            ),
        }

        query_text = (
            f'"{topic}" '
            f'{level_terms.get(level, "")} '
            "educational"
        )

        results = (
            await youtube_service.search_videos(
                query=query_text,
                language=language,
                limit=50,
            )
        )

        videos = (
            await youtube_service
            .enrich_search_results(
                results
            )
        )

        return {
            **topic_info,
            "videos": videos[:limit],
        }


topic_search_service = (
    TopicSearchService()
)