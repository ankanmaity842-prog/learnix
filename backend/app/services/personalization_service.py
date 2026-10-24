
from typing import Any


class PersonalizationService:
    VALID_LEVELS = {
        "beginner",
        "intermediate",
        "advanced",
    }

    def build_profile(
        self,
        learner_level: str,
        preferred_language: str,
        knowledge: dict[str, float],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        level = self._normalize_level(learner_level)
        language = self._normalize_language(preferred_language)

        normalized_knowledge = {
            str(topic).strip().casefold(): self._normalize_score(score)
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

        watched_video_ids = set()
        history_topics = set()

        for item in history:
            if not isinstance(item, dict):
                continue

            video_id = item.get("video_id") or item.get("youtube_video_id")
            if video_id:
                watched_video_ids.add(str(video_id).strip())

            topic = item.get("topic")
            if topic:
                history_topics.add(str(topic).strip().casefold())

        return {
            "level": level,
            "language": language,
            "knowledge": normalized_knowledge,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "completed_topics": completed_topics,
            "learning_sessions": len(history),
            "watched_video_ids": watched_video_ids,
            "history_topics": history_topics,
        }

    def match_video(
        self,
        video: dict[str, Any],
        profile: dict[str, Any],
    ) -> float:
        learner_level = self._normalize_level(
            profile.get("level", "beginner")
        )

        video_level = self._normalize_level(
            video.get("difficulty", "intermediate")
        )

        score = self._level_match(
            learner_level,
            video_level,
        ) * 0.50

        learner_language = self._normalize_language(
            profile.get("language", "en")
        )

        video_language = self._normalize_language(
            video.get("language", "en")
        )

        if learner_language == video_language:
            score += 0.25

        visual_simplicity = self._normalize_score(
            video.get("visual_simplicity", 0.5)
        )

        transcript_simplicity = self._normalize_score(
            video.get("transcript_simplicity", 0.5)
        )

        score += visual_simplicity * 0.15
        score += transcript_simplicity * 0.10

        video_id = str(
            video.get("video_id")
            or video.get("youtube_video_id")
            or ""
        ).strip()

        watched_ids = profile.get("watched_video_ids", set())

        if video_id and video_id in watched_ids:
            score *= 0.75

        return round(max(0.0, min(score, 1.0)), 4)

    @classmethod
    def _normalize_level(cls, value: Any) -> str:
        level = str(value or "beginner").strip().lower()

        if level not in cls.VALID_LEVELS:
            return "beginner"

        return level

    @staticmethod
    def _normalize_language(value: Any) -> str:
        return str(value or "en").strip().lower() or "en"

    @staticmethod
    def _level_match(
        learner_level: str,
        video_level: str,
    ) -> float:
        levels = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
        }

        difference = abs(
            levels[learner_level] - levels[video_level]
        )

        if difference == 0:
            return 1.0

        if difference == 1:
            return 0.6

        return 0.3

    @staticmethod
    def _normalize_score(value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.5

        return max(0.0, min(score, 1.0))


personalization_service = PersonalizationService()

