from pathlib import Path
from typing import Any

import joblib


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "ml_models"
    / "recommendation"
    / "recommendation_model.pkl"
)


class RecommendationModel:

    def __init__(self):
        self.model = None

        if MODEL_PATH.exists():
            self.model = joblib.load(
                MODEL_PATH
            )

    def predict(
        self,
        features: list[float],
    ) -> float:

        if self.model is None:
            return self._fallback(features)

        try:
            prediction = self.model.predict(
                [features]
            )[0]

            return float(
                max(
                    0.0,
                    min(
                        1.0,
                        prediction,
                    ),
                )
            )

        except Exception:
            return self._fallback(features)

    @staticmethod
    def _fallback(
        features: list[float],
    ) -> float:

        if not features:
            return 0.0

        return sum(features) / len(features)