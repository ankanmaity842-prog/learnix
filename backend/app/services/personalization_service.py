from typing import Any


class PersonalizationService:

    def build_profile(
        self,
        learner_level: str,
        preferred_language: str,
        knowledge: dict[str, float],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:

        normalized_knowledge = {
            str(topic).strip(): self._normalize_score(
                score
            )
            for topic, score in knowledge.items()
            if str(topic).strip()
        }

        strong_topics = [
            topic
            for topic, score in normalized_knowledge.items()
            if score >= 0.8
        ]

        weak_topics = [
            topic
            for topic, score in normalized_knowledge.items()
            if score < 0.5
        ]

        completed_topics = [
            topic
            for topic, score in normalized_knowledge.items()
            if score >= 0.7
        ]

        return {
            "level": learner_level,
            "language": preferred_language,
            "knowledge": normalized_knowledge,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "completed_topics": completed_topics,
            "learning_sessions": len(history),
        }

    def match_video(
        self,
        video: dict[str, Any],
        profile: dict[str, Any],
    ) -> float:

        score = 0.0

        learner_level = profile.get(
            "level",
            "beginner",
        )

        video_level = video.get(
            "difficulty",
            "intermediate",
        )

        level_score = self._level_match(
            learner_level,
            video_level,
        )

        score += level_score * 0.5

        video_language = video.get(
            "language",
            "en",
        )

        if video_language == profile.get(
            "language",
            "en",
        ):
            score += 0.25

        visual_simplicity = self._normalize_score(
            video.get(
                "visual_simplicity",
                0.5,
            )
        )

        score += visual_simplicity * 0.15

        transcript_simplicity = self._normalize_score(
            video.get(
                "transcript_simplicity",
                0.5,
            )
        )

        score += transcript_simplicity * 0.10

        return round(
            min(score, 1.0),
            4,
        )

    @staticmethod
    def _level_match(
        learner_level: str,
        video_level: str,
    ) -> float:

        learner_level = learner_level.lower()
        video_level = video_level.lower()

        if learner_level == video_level:
            return 1.0

        levels = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
        }

        learner_index = levels.get(
            learner_level,
            1,
        )

        video_index = levels.get(
            video_level,
            1,
        )

        difference = abs(
            learner_index - video_index
        )

        if difference == 1:
            return 0.6

        return 0.3

    @staticmethod
    def _normalize_score(
        value: Any,
    ) -> float:

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.5

        return max(
            0.0,
            min(value, 1.0),
        )


personalization_service = PersonalizationService()