import re
from typing import Any

from app.services.personalization_service import personalization_service


class RecommendationService:
    LEVEL_KEYWORDS = {
        "beginner": (
            "beginner", "basics", "basic", "from scratch",
            "introduction", "intro", "fundamentals",
            "for beginners", "zero to hero",
        ),
        "intermediate": (
            "intermediate", "practical", "projects",
            "real world", "hands on", "implementation",
            "practice", "examples",
        ),
        "advanced": (
            "advanced", "expert", "deep dive", "internals",
            "architecture", "optimization", "system design",
            "production",
        ),
    }

    OTHER_LEVEL_TERMS = {
        "beginner": (
            "advanced tutorial", "expert level", "deep dive",
            "system design", "internals",
        ),
        "intermediate": (
            "absolute beginner", "from scratch for beginners",
            "advanced tutorial", "expert level", "deep dive",
        ),
        "advanced": (
            "absolute beginner", "beginner basics",
            "from scratch", "introduction to", "intro to",
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
        profile = personalization_service.build_profile(
            learner_level=learner_level,
            preferred_language=preferred_language,
            knowledge=knowledge or {},
            history=history or [],
        )

        ranked = []
        for video in videos:
            topic_score = self._topic_relevance(video, topic)
            if topic and topic_score < 0.20:
                continue

            engagement = self._engagement_score(video)
            level_score = self._level_score(video, learner_level)
            user_match = self._safe_float(
                personalization_service.match_video(
                    video=video,
                    profile=profile,
                )
            )

            score = (
                topic_score * 0.45
                + engagement * 0.25
                + level_score * 0.15
                + user_match * 0.05
                + (0.10 if video.get("is_indian_creator") else 0.0)
            )

            ranked.append({
                **video,
                "topic_relevance": round(topic_score, 4),
                "engagement_score": round(engagement, 4),
                "level_score": round(level_score, 4),
                "user_match": round(user_match, 4),
                "recommendation_score": round(min(score, 1.0), 4),
                "reason": self._build_reason(
                    video, learner_level, preferred_language
                ),
            })

        # Indian creators first; within that group, topic score and views
        # determine the order. For Hindi/Bengali, strict filtering belongs
        # in the router before this ranking stage.
        ranked.sort(
            key=lambda item: (
                bool(item.get("is_indian_creator")),
                item.get("topic_relevance", 0),
                self._safe_int(item.get("views")),
                item.get("recommendation_score", 0),
            ),
            reverse=True,
        )
        return ranked

    def select_level_videos(
        self,
        videos: list[dict[str, Any]],
        level: str,
        limit: int,
        used_video_ids: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        used_video_ids = used_video_ids or set()
        selected = []
        seen_ids = set()
        seen_titles = set()

        for video in videos:
            video_id = str(video.get("video_id") or "")
            title = self._normalize_title(video.get("title", ""))

            if not video_id or not title:
                continue
            if video_id in used_video_ids or video_id in seen_ids:
                continue
            if title in seen_titles:
                continue
            if self._looks_like_other_level(video, level):
                continue

            seen_ids.add(video_id)
            seen_titles.add(title)
            selected.append(video)

            if len(selected) >= limit:
                break

        return selected

    @classmethod
    def _looks_like_other_level(
        cls,
        video: dict[str, Any],
        requested_level: str,
    ) -> bool:
        title = str(video.get("title", "")).casefold()
        return any(
            phrase in title
            for phrase in cls.OTHER_LEVEL_TERMS.get(
                requested_level, ()
            )
        )

    @classmethod
    def _level_score(
        cls,
        video: dict[str, Any],
        level: str,
    ) -> float:
        title = str(video.get("title", "")).casefold()
        matches = sum(
            1 for keyword in cls.LEVEL_KEYWORDS.get(level, ())
            if keyword in title
        )
        return min(1.0, 0.4 + matches * 0.15)

    @staticmethod
    def _topic_relevance(
        video: dict[str, Any],
        topic: str | None,
    ) -> float:
        if not topic:
            return 0.5

        topic_words = {
            word.casefold()
            for word in re.findall(r"\w+", topic)
            if len(word) > 2
        }
        if not topic_words:
            return 0.5

        text = " ".join([
            str(video.get("title", "")),
            str(video.get("description", "")),
        ]).casefold()

        matched = sum(1 for word in topic_words if word in text)
        return matched / len(topic_words)

    @staticmethod
    def _engagement_score(video: dict[str, Any]) -> float:
        views = RecommendationService._safe_int(video.get("views"))
        likes = RecommendationService._safe_int(video.get("likes"))

        if views <= 0:
            return 0.0

        view_score = min(views / 1_000_000, 1.0)
        like_ratio = min(likes / views, 0.10) / 0.10
        return 0.6 * view_score + 0.4 * like_ratio

    @staticmethod
    def _normalize_title(title: str) -> str:
        return " ".join(
            re.sub(r"[^\w\s]", "", title.casefold()).split()
        )

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return max(0.0, min(float(value or 0), 1.0))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _build_reason(
        video: dict[str, Any],
        level: str,
        language: str,
    ) -> str:
        reasons = [f"{level} learning level"]
        if video.get("is_indian_creator"):
            reasons.append("Indian creator")
        if video.get("views"):
            reasons.append("view-count popularity")
        return "Recommended for " + ", ".join(reasons) + "."


recommendation_service = RecommendationService()