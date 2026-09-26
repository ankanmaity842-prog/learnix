from app.ai.knowledge_gap_model import KnowledgeGapModel


def test_knowledge_gap_model():
    model = KnowledgeGapModel()

    result = model.predict(
        target_topic="Machine Learning",
        learner_knowledge={
            "Python": 0.9,
            "Linear Algebra": 0.2,
            "Statistics": 0.3,
        },
    )

    assert "missing_topics" in result
    assert "readiness_score" in result
    assert "ready" in result

    assert isinstance(
        result["missing_topics"],
        list,
    )

    assert 0.0 <= result["readiness_score"] <= 1.0