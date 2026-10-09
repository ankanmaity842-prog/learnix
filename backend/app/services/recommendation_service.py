from typing import Any

from app.services.personalization_service import (
    personalization_service,
)


class RecommendationService:

    LEVEL_COUNTS = {
        "beginner": (40, 50),
        "intermediate": (20, 30),
        "advanced": (10, 15),
    }

    LEVEL_KEYWORDS = {
        "beginner": (
            "beginner",
            "basics",
            "basic",
            "from scratch",
            "introduction",
            "intro",
            "fundamentals",
            "easy",
            "zero to hero",
            "for beginners",
        ),
        "intermediate": (
            "intermediate",
            "practical",
            "projects",
            "project",
            "real world",
            "hands on",
            "implementation",
            "practice",
            "examples",
        ),
        "advanced": (
            "advanced",
            "expert",
            "deep dive",
            "internals",
            "architecture",
            "optimization",
            "system design",
            "production",
            "advanced concepts",
        ),
    }

    def rank_videos(
        self,
        videos: list[dict[str, Any]],
        topic: str | None = None,
        learner_level: str = "beginner",
        preferred_language: str = "en",
        knowledge: dict[str, float] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:

        knowledge = knowledge or {}
        history = history or []

        profile = personalization_service.build_profile(
            learner_level=learner_level,
            preferred_language=preferred_language,
            knowledge=knowledge,
            history=history,
        )

        ranked = []

        for video in videos:

            topic_relevance = self._topic_relevance(
                video,
                topic,
            )

            transcript_simplicity = self._get_score(
                video,
                "transcript_simplicity",
                0.5,
            )

            visual_simplicity = self._get_score(
                video,
                "visual_simplicity",
                0.5,
            )

            explanation_structure = self._get_score(
                video,
                "explanation_structure",
                0.5,
            )

            user_match = personalization_service.match_video(
                video=video,
                profile=profile,
            )

            duration_score = self._duration_score(
                video.get("duration"),
                learner_level,
            )

            engagement_score = self._engagement_score(
                video
            )

            level_score = self._level_keyword_score(
                video,
                learner_level,
            )

            indian_score = (
                1.0
                if video.get(
                    "is_indian_creator",
                    False,
                )
                else 0.0
            )

            language_score = (
                1.0
                if video.get(
                    "is_language_creator",
                    False,
                )
                else 0.0
            )

            score = (
                topic_relevance * 0.35
                + engagement_score * 0.20
                + indian_score * 0.12
                + language_score * 0.12
                + level_score * 0.10
                + transcript_simplicity * 0.04
                + visual_simplicity * 0.03
                + explanation_structure * 0.02
                + user_match * 0.01
                + duration_score * 0.01
            )

            ranked_video = {
                **video,
                "topic_relevance": round(
                    topic_relevance,
                    4,
                ),
                "transcript_simplicity": round(
                    transcript_simplicity,
                    4,
                ),
                "visual_simplicity": round(
                    visual_simplicity,
                    4,
                ),
                "explanation_structure": round(
                    explanation_structure,
                    4,
                ),
                "user_match": round(
                    user_match,
                    4,
                ),
                "duration_score": round(
                    duration_score,
                    4,
                ),
                "engagement_score": round(
                    engagement_score,
                    4,
                ),
                "level_score": round(
                    level_score,
                    4,
                ),
                "indian_creator_score": (
                    indian_score
                ),
                "language_creator_score": (
                    language_score
                ),
                "recommendation_score": round(
                    max(
                        0.0,
                        min(score, 1.0),
                    ),
                    4,
                ),
            }

            ranked_video["reason"] = (
                self._build_reason(
                    ranked_video,
                    learner_level,
                    preferred_language,
                )
            )

            ranked.append(
                ranked_video
            )

        return sorted(
            ranked,
            key=lambda item: (
                item.get(
                    "is_language_creator",
                    False,
                ),
                item.get(
                    "is_indian_creator",
                    False,
                ),
                self._safe_int(
                    item.get(
                        "views",
                        0,
                    )
                ),
                item.get(
                    "recommendation_score",
                    0.0,
                ),
            ),
            reverse=True,
        )

    def select_level_videos(
        self,
        videos: list[dict[str, Any]],
        level: str,
        limit: int,
        used_video_ids: set[str] | None = None,
    ) -> list[dict[str, Any]]:

        used_video_ids = (
            used_video_ids or set()
        )

        level = level.lower()

        candidates = []

        for video in videos:

            video_id = str(
                video.get(
                    "video_id",
                    "",
                )
            )

            if not video_id:
                continue

            if video_id in used_video_ids:
                continue

            if self._looks_like_other_level(
                video,
                level,
            ):
                continue

            candidates.append(video)

        # Remove duplicate titles.
        title_seen = set()
        unique = []

        for video in candidates:

            title = self._normalize_title(
                video.get(
                    "title",
                    "",
                )
            )

            if not title:
                continue

            if title in title_seen:
                continue

            title_seen.add(title)
            unique.append(video)

        # Strongest ranking:
        # language creator -> Indian creator -> views.
        unique.sort(
            key=lambda item: (
                item.get(
                    "is_language_creator",
                    False,
                ),
                item.get(
                    "is_indian_creator",
                    False,
                ),
                self._safe_int(
                    item.get(
                        "views",
                        0,
                    )
                ),
                item.get(
                    "recommendation_score",
                    0.0,
                ),
            ),
            reverse=True,
        )

        return unique[:limit]

    @classmethod
    def _looks_like_other_level(
        cls,
        video: dict[str, Any],
        requested_level: str,
    ) -> bool:

        text = " ".join(
            [
                str(
                    video.get(
                        "title",
                        "",
                    )
                ),
                str(
                    video.get(
                        "description",
                        "",
                    )
                ),
            ]
        ).lower()

        other_levels = {
            "beginner": (
                "advanced",
                "expert",
                "deep dive",
                "system design",
                "internals",
            ),
            "intermediate": (
                "absolute beginner",
                "from scratch",
                "basics",
                "advanced",
                "expert",
                "deep dive",
            ),
            "advanced": (
                "absolute beginner",
                "beginner basics",
                "from scratch",
                "introduction",
                "intro to",
            ),
        }

        return any(
            keyword in text
            for keyword in other_levels.get(
                requested_level,
                (),
            )
        )

    @classmethod
    def _level_keyword_score(
        cls,
        video: dict[str, Any],
        level: str,
    ) -> float:

        text = " ".join(
            [
                str(
                    video.get(
                        "title",
                        "",
                    )
                ),
                str(
                    video.get(
                        "description",
                        "",
                    )
                ),
            ]
        ).lower()

        keywords = cls.LEVEL_KEYWORDS.get(
            level,
            (),
        )

        if not keywords:
            return 0.5

        matches = sum(
            1
            for keyword in keywords
            if keyword in text
        )

        return min(
            1.0,
            0.35 + matches * 0.15,
        )

    @staticmethod
    def _topic_relevance(
        video: dict[str, Any],
        topic: str | None,
    ) -> float:

        if not topic:
            return 0.5

        topic_words = {
            word.lower()
            for word in topic.split()
            if len(word) > 2
        }

        text = " ".join(
            [
                str(
                    video.get(
                        "title",
                        "",
                    )
                ),
                str(
                    video.get(
                        "description",
                        "",
                    )
                ),
            ]
        ).lower()

        if not topic_words:
            return 0.5

        matches = sum(
            1
            for word in topic_words
            if word in text
        )

        return min(
            1.0,
            matches / len(topic_words),
        )

    @staticmethod
    def _get_score(
        video: dict[str, Any],
        key: str,
        default: float,
    ) -> float:

        try:
            value = float(
                video.get(
                    key,
                    default,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            value = default

        return max(
            0.0,
            min(
                value,
                1.0,
            ),
        )

    @staticmethod
    def _duration_score(
        duration: str | None,
        learner_level: str,
    ) -> float:

        if not duration:
            return 0.5

        try:
            seconds = (
                RecommendationService
                ._parse_duration(
                    duration
                )
            )
        except ValueError:
            return 0.5

        if learner_level == "beginner":
            if seconds <= 900:
                return 1.0
            if seconds <= 1800:
                return 0.8
            if seconds <= 3600:
                return 0.6
            return 0.4

        if learner_level == "intermediate":
            if seconds <= 1800:
                return 0.9
            if seconds <= 3600:
                return 1.0
            if seconds <= 5400:
                return 0.8
            return 0.6

        if seconds <= 3600:
            return 0.9

        return 1.0

    @staticmethod
    def _parse_duration(
        duration: str,
    ) -> int:

        duration = duration.replace(
            "PT",
            "",
        )

        hours = 0
        minutes = 0
        seconds = 0
        number = ""

        for char in duration:

            if char.isdigit():
                number += char
                continue

            if char == "H":
                hours = int(
                    number or 0
                )

            elif char == "M":
                minutes = int(
                    number or 0
                )

            elif char == "S":
                seconds = int(
                    number or 0
                )

            number = ""

        return (
            hours * 3600
            + minutes * 60
            + seconds
        )

    @staticmethod
    def _engagement_score(
        video: dict[str, Any],
    ) -> float:

        views = RecommendationService._safe_int(
            video.get(
                "views",
                0,
            )
        )

        likes = RecommendationService._safe_int(
            video.get(
                "likes",
                0,
            )
        )

        if views <= 0:
            return 0.0

        like_ratio = min(
            likes / views,
            0.1,
        )

        like_score = (
            like_ratio / 0.1
        )

        view_score = min(
            1.0,
            views / 1_000_000,
        )

        return round(
            like_score * 0.4
            + view_score * 0.6,
            4,
        )

    @staticmethod
    def _normalize_title(
        title: str,
    ) -> str:

        return " ".join(
            title.lower()
            .strip()
            .split()
        )

    @staticmethod
    def _safe_int(
        value: Any,
    ) -> int:

        try:
            return max(
                0,
                int(value or 0),
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _build_reason(
        video: dict[str, Any],
        level: str,
        language: str,
    ) -> str:

        reasons = []

        if video.get(
            "is_language_creator"
        ):
            reasons.append(
                f"{language} language creator"
            )

        if video.get(
            "is_indian_creator"
        ):
            reasons.append(
                "Indian creator"
            )

        if video.get(
            "views",
            0,
        ):
            reasons.append(
                "high-view educational video"
            )

        if video.get(
            "level_score",
            0,
        ) >= 0.6:
            reasons.append(
                f"{level} level match"
            )

        if not reasons:
            reasons.append(
                "topic and learning-level match"
            )

        return (
            "Recommended because it is "
            + ", ".join(reasons)
            + "."
        )


recommendation_service = (
    RecommendationService()
)