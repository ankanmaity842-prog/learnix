from typing import Any

from app.ai.difficulty_model import DifficultyModel


class DifficultyService:

    def __init__(self):
        self.model = DifficultyModel()

    def analyze(
        self,
        text: str,
        features: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        features = features or {}

        prediction = self.model.predict(
            text=text,
            features=features,
        )

        level = prediction.get(
            "level",
            "intermediate",
        )

        if level == "medium":
            level = "intermediate"

        try:
            score = float(
                prediction.get(
                    "score",
                    0.5,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            score = 0.5

        try:
            confidence = float(
                prediction.get(
                    "confidence",
                    0.0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        return {
            "level": level,
            "score": round(
                max(0.0, min(score, 1.0)),
                4,
            ),
            "confidence": round(
                max(0.0, min(confidence, 1.0)),
                4,
            ),
        }


difficulty_service = DifficultyService()