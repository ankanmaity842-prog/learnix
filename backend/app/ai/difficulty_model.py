from pathlib import Path
from typing import Any

import joblib


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "ml_models"
    / "difficulty"
    / "difficulty_model.pkl"
)


class DifficultyModel:

    def __init__(self):
        self.model = None

        if MODEL_PATH.exists():
            self.model = joblib.load(
                MODEL_PATH
            )

    def predict(
        self,
        text: str,
        features: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        if self.model is None:
            return self._fallback(text)

        try:
            prediction = self.model.predict(
                [text]
            )[0]

            confidence = 0.0

            if hasattr(
                self.model,
                "predict_proba",
            ):
                probabilities = (
                    self.model.predict_proba(
                        [text]
                    )[0]
                )

                confidence = float(
                    max(probabilities)
                )

            return {
                "level": str(prediction),
                "score": self._level_score(
                    str(prediction)
                ),
                "confidence": confidence,
            }

        except Exception:
            return self._fallback(text)

    @staticmethod
    def _level_score(
        level: str,
    ) -> float:

        scores = {
            "beginner": 0.25,
            "easy": 0.25,
            "medium": 0.50,
            "intermediate": 0.60,
            "hard": 0.80,
            "advanced": 0.90,
        }

        return scores.get(
            level.lower(),
            0.50,
        )

    @staticmethod
    def _fallback(
        text: str,
    ) -> dict[str, Any]:

        words = len(text.split())

        if words < 30:
            level = "beginner"
        elif words < 100:
            level = "intermediate"
        else:
            level = "advanced"

        return {
            "level": level,
            "score": DifficultyModel._level_score(
                level
            ),
            "confidence": 0.0,
        }