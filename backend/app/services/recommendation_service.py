import re
from typing import Any

from app.services.personalization_service import (
    personalization_service,
)


class RecommendationService:

    ENTERTAINMENT_KEYWORDS = {
        "movie",
        "movies",
        "film",
        "films",
        "song",
        "songs",
        "music",
        "lyrics",
        "dance",
        "dancing",
        "comedy",
        "funny",
        "vlog",
        "vlogging",
        "prank",
        "roast",
        "reaction",
        "reactions",
        "gaming",
        "gameplay",
        "shorts",
        "short",
        "trailer",
        "celebrity",
        "entertainment",
        "web series",
        "webseries",
    }

    UNRELATED_TECHNOLOGY_MAP = {
        "python": {
            "javascript",
            "java",
            "c++",
            "cpp",
            "c#",
            "csharp",
            "php",
            "ruby",
            "kotlin",
            "swift",
            "golang",
            "go programming",
            "rust",
        },
        "javascript": {
            "python",
            "java",
            "c++",
            "cpp",
            "c#",
            "csharp",
            "php",
        },
        "java": {
            "python",
            "javascript",
            "c++",
            "cpp",
            "c#",
            "csharp",
            "php",
        },
        "react": {
            "angular",
            "vue",
            "python",
            "java",
            "c++",
        },
        "angular": {
            "react",
            "vue",
            "python",
            "java",
        },
        "vue": {
            "react",
            "angular",
            "python",
            "java",
        },
    }

    def calculate_score(
        self,
        topic_relevance: float,
        transcript_simplicity: float,
        visual_simplicity: float,
        explanation_structure: float,
        user_match: float,
        duration_score: float,
        engagement_score: float,
    ) -> float:

        score = (
            topic_relevance * 0.40
            + transcript_simplicity * 0.10
            + visual_simplicity * 0.10
            + explanation_structure * 0.05
            + user_match * 0.15
            + duration_score * 0.05
            + engagement_score * 0.15
        )

        return round(
            max(0.0, min(score, 1.0)),
            4,
        )

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

        topic = (topic or "").strip()

        ranked = []

        for video in videos:

            if self._is_entertainment(video):
                continue

            if not self._is_topic_relevant(
                video,
                topic,
            ):
                continue

            topic_relevance = (
                self._topic_relevance(
                    video,
                    topic,
                )
            )

            transcript_simplicity = (
                self._get_score(
                    video,
                    "transcript_simplicity",
                    0.5,
                )
            )

            visual_simplicity = (
                self._get_score(
                    video,
                    "visual_simplicity",
                    0.5,
                )
            )

            explanation_structure = (
                self._get_score(
                    video,
                    "explanation_structure",
                    0.5,
                )
            )

            user_match = (
                personalization_service.match_video(
                    video=video,
                    profile=profile,
                )
            )

            duration_score = (
                self._duration_score(
                    video.get("duration"),
                    learner_level,
                )
            )

            engagement_score = (
                self._engagement_score(video)
            )

            score = self.calculate_score(
                topic_relevance=topic_relevance,
                transcript_simplicity=(
                    transcript_simplicity
                ),
                visual_simplicity=(
                    visual_simplicity
                ),
                explanation_structure=(
                    explanation_structure
                ),
                user_match=user_match,
                duration_score=duration_score,
                engagement_score=engagement_score,
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
                "recommendation_score": score,
                "difficulty": learner_level,
            }

            ranked_video["reason"] = (
                self._build_reason(
                    ranked_video,
                    learner_level,
                )
            )

            ranked.append(ranked_video)

        def sort_key(
            item: dict[str, Any],
        ):
            views = self._safe_int(
                item.get("views", 0)
            )

            indian = bool(
                item.get(
                    "is_indian_creator",
                    False,
                )
            )

            score = float(
                item.get(
                    "recommendation_score",
                    0.0,
                )
            )

            # Indian educational creators first.
            # Then popularity.
            # Then recommendation quality.
            return (
                indian,
                views,
                score,
            )

        return sorted(
            ranked,
            key=sort_key,
            reverse=True,
        )

    def _is_topic_relevant(
        self,
        video: dict[str, Any],
        topic: str,
    ) -> bool:

        if not topic:
            return True

        title = str(
            video.get("title", "")
        ).lower()

        description = str(
            video.get("description", "")
        ).lower()

        channel = str(
            video.get("channel", "")
        ).lower()

        text = (
            f"{title} "
            f"{description} "
            f"{channel}"
        )

        topic_normalized = (
            topic.lower().strip()
        )

        # Exact phrase gets priority.
        if topic_normalized in title:
            return True

        if topic_normalized in description:
            return True

        # Check important individual terms.
        topic_words = [
            word
            for word in re.findall(
                r"[a-zA-Z0-9+#.]+",
                topic_normalized,
            )
            if len(word) >= 2
        ]

        if not topic_words:
            return True

        matches = sum(
            1
            for word in topic_words
            if word in text
        )

        if matches == len(topic_words):
            return True

        # Special protection against unrelated programming
        # languages and frameworks.
        unrelated = (
            self.UNRELATED_TECHNOLOGY_MAP.get(
                topic_normalized,
                set(),
            )
        )

        for keyword in unrelated:
            if keyword in title:
                return False

        return matches >= max(
            1,
            len(topic_words) // 2,
        )

    def _topic_relevance(
        self,
        video: dict[str, Any],
        topic: str,
    ) -> float:

        if not topic:
            return 0.5

        title = str(
            video.get("title", "")
        ).lower()

        description = str(
            video.get("description", "")
        ).lower()

        topic = topic.lower().strip()

        if topic in title:
            return 1.0

        if topic in description:
            return 0.9

        topic_words = [
            word
            for word in re.findall(
                r"[a-zA-Z0-9+#.]+",
                topic,
            )
            if len(word) >= 2
        ]

        if not topic_words:
            return 0.5

        matches = sum(
            1
            for word in topic_words
            if word in title
        )

        return min(
            0.85,
            0.45
            + (
                matches
                / len(topic_words)
            )
            * 0.4,
        )

    def _is_entertainment(
        self,
        video: dict[str, Any],
    ) -> bool:

        title = str(
            video.get("title", "")
        ).lower()

        description = str(
            video.get("description", "")
        ).lower()

        combined = (
            f"{title} {description}"
        )

        return any(
            keyword in combined
            for keyword in self.ENTERTAINMENT_KEYWORDS
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
            min(value, 1.0),
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
                return 0.85

            if seconds <= 3600:
                return 0.65

            return 0.4

        if learner_level == "intermediate":

            if seconds <= 1800:
                return 0.85

            if seconds <= 3600:
                return 1.0

            if seconds <= 5400:
                return 0.85

            return 0.65

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
                hours = int(number or 0)

            elif char == "M":
                minutes = int(number or 0)

            elif char == "S":
                seconds = int(number or 0)

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

        views = (
            RecommendationService
            ._safe_int(
                video.get(
                    "views",
                    0,
                )
            )
        )

        likes = (
            RecommendationService
            ._safe_int(
                video.get(
                    "likes",
                    0,
                )
            )
        )

        if views <= 0:
            return 0.3

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
    def _build_reason(
        video: dict[str, Any],
        learner_level: str,
    ) -> str:

        reasons = []

        if video[
            "topic_relevance"
        ] >= 0.85:
            reasons.append(
                "strong topic match"
            )

        if video[
            "user_match"
        ] >= 0.7:
            reasons.append(
                f"matches {learner_level} level"
            )

        if video.get(
            "is_indian_creator",
            False,
        ):
            reasons.append(
                "Indian educational creator"
            )

        if video.get(
            "views",
            0,
        ) > 0:
            reasons.append(
                "high popularity"
            )

        if not reasons:
            reasons.append(
                "good educational match"
            )

        return (
            "Recommended because it has "
            + ", ".join(reasons)
            + "."
        )


recommendation_service = (
    RecommendationService()
)