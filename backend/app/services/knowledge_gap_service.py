from typing import Any

from app.ai.knowledge_gap_model import KnowledgeGapModel
from app.ai.knowledge_graph import knowledge_graph


class KnowledgeGapService:

    def __init__(self):
        self.model = KnowledgeGapModel()

    def detect(
        self,
        target_topic: str,
        learner_knowledge: dict[str, float],
    ) -> dict[str, Any]:

        target_topic = target_topic.strip()

        prerequisites = knowledge_graph.get_prerequisites(
            target_topic
        )

        result = self.model.predict(
            target_topic=target_topic,
            learner_knowledge=learner_knowledge,
            prerequisites=prerequisites,
        )

        return {
            "target_topic": target_topic,
            "prerequisites": prerequisites,
            "ready": result.get(
                "ready",
                False,
            ),
            "readiness_score": result.get(
                "readiness_score",
                0.0,
            ),
            "missing_topics": result.get(
                "missing_topics",
                [],
            ),
        }


knowledge_gap_service = KnowledgeGapService()