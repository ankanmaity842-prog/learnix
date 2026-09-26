from app.ai.recommendation_model import RecommendationModel


def test_recommendation_model_returns_score():
    model = RecommendationModel()

    result = model.predict(
        {
            "relevance": 0.9,
            "simplicity": 0.8,
            "visual_simplicity": 0.7,
            "structure": 0.8,
            "knowledge_match": 0.9,
            "duration_score": 0.7,
            "engagement": 0.8,
        }
    )

    assert 0.0 <= result["score"] <= 1.0