from app.ai.difficulty_model import DifficultyModel


def test_difficulty_model_fallback():
    model = DifficultyModel()

    result = model.predict(
        "Machine learning is the process of teaching computers using data."
    )

    assert "level" in result
    assert "confidence" in result
    assert result["level"] in {
        "beginner",
        "intermediate",
        "advanced",
    }

    assert 0.0 <= result["confidence"] <= 1.0