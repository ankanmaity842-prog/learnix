from app.services.personalization_service import (
    PersonalizationService,
)


def test_build_profile():
    service = PersonalizationService()

    profile = service.build_profile(
        learner_level="beginner",
        preferred_language="en",
        knowledge={
            "Python": 0.9,
            "Machine Learning": 0.3,
            "SQL": 0.7,
        },
        history=[
            {
                "topic": "Python",
            },
            {
                "topic": "SQL",
            },
        ],
    )

    assert profile["level"] == "beginner"
    assert profile["language"] == "en"
    assert profile["learning_sessions"] == 2

    assert "Python" in profile["strong_topics"]
    assert "Machine Learning" in profile["weak_topics"]
    assert "SQL" in profile["completed_topics"]


def test_profile_score_normalization():
    service = PersonalizationService()

    profile = service.build_profile(
        learner_level="beginner",
        preferred_language="en",
        knowledge={
            "Python": 2.0,
            "SQL": -1.0,
        },
        history=[],
    )

    assert profile["knowledge"]["Python"] == 1.0
    assert profile["knowledge"]["SQL"] == 0.0


def test_exact_level_match():
    service = PersonalizationService()

    score = service._level_match(
        "beginner",
        "beginner",
    )

    assert score == 1.0


def test_adjacent_level_match():
    service = PersonalizationService()

    score = service._level_match(
        "beginner",
        "intermediate",
    )

    assert score == 0.6


def test_distant_level_match():
    service = PersonalizationService()

    score = service._level_match(
        "beginner",
        "advanced",
    )

    assert score == 0.3


def test_video_match():
    service = PersonalizationService()

    profile = service.build_profile(
        learner_level="beginner",
        preferred_language="en",
        knowledge={},
        history=[],
    )

    video = {
        "difficulty": "beginner",
        "language": "en",
        "visual_simplicity": 0.9,
        "transcript_simplicity": 0.9,
    }

    score = service.match_video(
        video=video,
        profile=profile,
    )

    assert 0.0 <= score <= 1.0
    assert score > 0.7