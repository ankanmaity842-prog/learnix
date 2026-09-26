from typing import Any

from app.ai.knowledge_graph import knowledge_graph


class LearningPathService:

    def build_path(
        self,
        target_topic: str,
        missing_topics: list[str] | None = None,
        learner_level: str = "beginner",
    ) -> dict[str, Any]:

        target_topic = target_topic.strip()

        missing_topics = missing_topics or []

        graph_path = knowledge_graph.get_learning_path(
            target_topic
        )

        ordered_topics = []

        for topic in graph_path:
            if topic not in ordered_topics:
                ordered_topics.append(topic)

        for topic in missing_topics:
            topic = topic.strip()

            if topic and topic not in ordered_topics:
                ordered_topics.insert(
                    0,
                    topic,
                )

        if target_topic in ordered_topics:
            ordered_topics.remove(
                target_topic
            )

        path = []

        for index, topic in enumerate(
            ordered_topics,
            start=1,
        ):
            path.append(
                {
                    "step": index,
                    "topic": topic,
                    "status": "recommended",
                }
            )

        path.append(
            {
                "step": len(path) + 1,
                "topic": target_topic,
                "status": "target",
            }
        )

        return {
            "target_topic": target_topic,
            "learner_level": learner_level,
            "path": path,
            "total_steps": len(path),
        }


learning_path_service = LearningPathService()