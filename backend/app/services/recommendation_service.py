from typing import Any

from app.services.personalization_service import personalization_service


class RecommendationService:
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
            topic_relevance * 0.35
            + transcript_simplicity * 0.20
            + visual_simplicity * 0.15
            + explanation_structure * 0.10
            + user_match * 0.10
            + duration_score * 0.05
            + engagement_score * 0.05
        )
        return round(max(0.0, min(score, 1.0)), 4)

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
            topic_relevance = self._get_score(video, "topic_relevance", 0.5)
            transcript_simplicity = self._get_score(
                video, "transcript_simplicity", 0.5
            )
            visual_simplicity = self._get_score(
                video, "visual_simplicity", 0.5
            )
            explanation_structure = self._get_score(
                video, "explanation_structure", 0.5
            )

            user_match = personalization_service.match_video(
                video=video,
                profile=profile,
            )
            duration_score = self._duration_score(
                video.get("duration"),
                learner_level,
            )
            engagement_score = self._engagement_score(video)

            score = self.calculate_score(
                topic_relevance=topic_relevance,
                transcript_simplicity=transcript_simplicity,
                visual_simplicity=visual_simplicity,
                explanation_structure=explanation_structure,
                user_match=user_match,
                duration_score=duration_score,
                engagement_score=engagement_score,
            )

            ranked_video = {
                **video,
                "topic_relevance": round(topic_relevance, 4),
                "transcript_simplicity": round(transcript_simplicity, 4),
                "visual_simplicity": round(visual_simplicity, 4),
                "explanation_structure": round(explanation_structure, 4),
                "user_match": round(user_match, 4),
                "duration_score": round(duration_score, 4),
                "engagement_score": round(engagement_score, 4),
                "recommendation_score": score,
            }
            ranked_video["reason"] = self._build_reason(
                ranked_video,
                learner_level,
            )
            ranked.append(ranked_video)

        def sort_key(item: dict[str, Any]):
            views = self._safe_int(item.get("views", 0))
            score = item.get("recommendation_score", 0.0)

            if preferred_language == "hi":
                return (
                    bool(item.get("is_indian_creator", False)),
                    views,
                    score,
                )

            if preferred_language == "bn":
                return (
                    bool(item.get("thumbnail_has_bengali", False)),
                    views,
                    score,
                )

            return (views, score)

        return sorted(ranked, key=sort_key, reverse=True)

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _get_score(
        video: dict[str, Any],
        key: str,
        default: float,
    ) -> float:
        try:
            value = float(video.get(key, default))
        except (TypeError, ValueError):
            value = default
        return max(0.0, min(value, 1.0))

    @staticmethod
    def _duration_score(
        duration: str | None,
        learner_level: str,
    ) -> float:
        if not duration:
            return 0.5

        try:
            seconds = RecommendationService._parse_duration(duration)
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
    def _parse_duration(duration: str) -> int:
        duration = duration.replace("PT", "")
        hours = minutes = seconds = 0
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

        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def _engagement_score(video: dict[str, Any]) -> float:
        views = RecommendationService._safe_int(video.get("views", 0))
        likes = RecommendationService._safe_int(video.get("likes", 0))

        if views == 0:
            return 0.5

        like_ratio = min(likes / views, 0.1)
        like_score = like_ratio / 0.1
        view_score = min(1.0, views / 1_000_000)

        return round(like_score * 0.6 + view_score * 0.4, 4)

    @staticmethod
    def _build_reason(
        video: dict[str, Any],
        learner_level: str,
    ) -> str:
        reasons = []

        if video["topic_relevance"] >= 0.7:
            reasons.append("high topic relevance")
        if video["transcript_simplicity"] >= 0.7:
            reasons.append("easy explanation")
        if video["visual_simplicity"] >= 0.7:
            reasons.append("clear visuals")
        if video["user_match"] >= 0.7:
            reasons.append(f"matches {learner_level} level")

        if not reasons:
            reasons.append("balanced match for your learning profile")

        return "Recommended because it has " + ", ".join(reasons) + "."


recommendation_service = RecommendationService()