from pathlib import Path
from typing import Any

import joblib
import numpy as np


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "ml_models"
    / "knowledge_gap"
    / "knowledge_gap_model.pkl"
)


class KnowledgeGapModel:

    def __init__(self):
        self.model = None

        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(
                    MODEL_PATH
                )
            except Exception:
                self.model = None

    def predict(
        self,
        target_topic: str,
        learner_knowledge: dict[str, float],
        prerequisites: list[str] | None = None,
    ) -> dict[str, Any]:

        prerequisites = prerequisites or []

        normalized = {
            str(topic).strip(): self._normalize_score(
                score
            )
            for topic, score in learner_knowledge.items()
            if str(topic).strip()
        }

        required_topics = [
            topic.strip()
            for topic in prerequisites
            if topic.strip()
        ]

        if not required_topics:
            required_topics = list(
                normalized.keys()
            )

        missing_topics = []

        scores = []

        for topic in required_topics:
            score = normalized.get(
                topic,
                0.0,
            )

            scores.append(score)

            if score < 0.5:
                missing_topics.append(topic)

        if scores:
            readiness = float(
                np.mean(scores)
            )
        else:
            readiness = 0.0

        return {
            "ready": readiness >= 0.7
            and not missing_topics,
            "readiness_score": round(
                readiness,
                4,
            ),
            "missing_topics": missing_topics,
        }

    @staticmethod
    def _normalize_score(
        score: Any,
    ) -> float:

        try:
            score = float(score)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(score, 1.0),
        )