from app.utils.scoring import (
    clamp_score,
    percentage,
    weighted_score,
)


def test_clamp_score():
    assert clamp_score(1.5) == 1.0
    assert clamp_score(-0.5) == 0.0
    assert clamp_score(0.5) == 0.5


def test_weighted_score():
    scores = {
        "relevance": 0.8,
        "difficulty": 0.6,
    }

    weights = {
        "relevance": 0.7,
        "difficulty": 0.3,
    }

    result = weighted_score(
        scores,
        weights,
    )

    assert round(result, 2) == 0.74


def test_percentage():
    assert percentage(0.75) == 75.0
    assert percentage(1.0) == 100.0
    assert percentage(0.0) == 0.0