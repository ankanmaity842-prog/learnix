
import re
from typing import Any

from app.services.personalization_service import personalization_service


class RecommendationService:
    LEVEL_KEYWORDS = {
        "beginner": (
            "beginner",
            "beginners",
            "beginner friendly",
            "beginner-level",
            "beginner level",
            "absolute beginner",
            "basic level",
            "basics for beginners",
            "from scratch",
            "no prior experience",
            "no previous experience",
            "introduction for beginners",
        ),
        "intermediate": (
            "intermediate",
            "intermediate-level",
            "intermediate level",
            "intermediate tutorial",
            "intermediate project",
            "beyond the basics",
            "prior knowledge required",
        ),
        "advanced": (
            "advanced",
            "advanced-level",
            "advanced level",
            "advanced tutorial",
            "advanced project",
            "expert-level",
            "expert level",
            "deep dive",
            "production-level",
            "production ready",
        ),
    }

    PROJECT_KEYWORDS = (
        "project",
        "projects",
        "build",
        "building",
        "implementation",
        "end-to-end",
        "end to end",
        "deploy",
        "deployment",
        "real-world application",
        "real world application",
    )

    TOPIC_ALIASES = {
        "css": ("css", "cascading style sheets"),
        "html": ("html", "hypertext markup language"),
        "js": ("javascript", "java script", "js"),
        "javascript": ("javascript", "java script", "js"),
        "react": ("react", "react.js", "reactjs"),
        "python": ("python",),
        "java": ("java", "java programming", "java language"),
        "c++": ("c++", "cpp", "c plus plus"),
        "c#": ("c#", "c sharp"),
        "sql": ("sql", "structured query language"),
        "machine learning": ("machine learning", "ml"),
        "artificial intelligence": (
            "artificial intelligence",
            "machine intelligence",
            "ai",
        ),
        "node.js": ("node.js", "nodejs", "node js"),
        "next.js": ("next.js", "nextjs", "next js"),
    }

    VALID_LEVELS = {"beginner", "intermediate", "advanced"}

    @staticmethod
    def _text(video: dict[str, Any]) -> str:
        return " ".join(
            str(video.get(field) or "")
            for field in ("title", "description")
        ).casefold()

    @staticmethod
    def _normalize_words(value: str) -> str:
        return " ".join(
            re.findall(r"\w+", str(value).casefold())
        )

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:
        text = str(text or "").casefold()
        phrase = str(phrase or "").casefold().strip()

        if not text or not phrase:
            return False

        # Normalize ordinary phrases by whitespace, but preserve symbols
        # so C++, C#, and Node.js can be handled explicitly.
        escaped = re.escape(phrase)
        escaped = escaped.replace(r"\ ", r"\s+")

        return re.search(
            rf"(?<!\w){escaped}(?!\w)",
            text,
        ) is not None

    @classmethod
    def matches_level(
        cls,
        video: dict[str, Any],
        requested_level: str,
    ) -> bool:
        requested_level = str(
            requested_level or ""
        ).strip().casefold()

        if requested_level not in cls.VALID_LEVELS:
            return False

        text = cls._text(video)
        matched_levels = {
            level
            for level, phrases in cls.LEVEL_KEYWORDS.items()
            if any(
                cls._contains_phrase(text, phrase)
                for phrase in phrases
            )
        }

        return matched_levels == {requested_level}

    @classmethod
    def _topic_relevance(
        cls,
        video: dict[str, Any],
        topic: str | None,
    ) -> float:
        if not topic or not topic.strip():
            return 0.5

        text = cls._text(video)

        if not text:
            return 0.0

        normalized_topic = cls._normalize_words(topic)

        if not normalized_topic:
            return 0.5

        aliases = cls.TOPIC_ALIASES.get(normalized_topic)

        if aliases:
            return (
                1.0
                if any(
                    cls._contains_phrase(text, alias)
                    for alias in aliases
                )
                else 0.0
            )

        words = [
            word
            for word in normalized_topic.split()
            if len(word) > 2
        ]

        if not words:
            return (
                1.0
                if cls._contains_phrase(text, topic)
                else 0.0
            )

        matched = sum(
            cls._contains_phrase(text, word)
            for word in words
        )

        return matched / len(words)

    def rank_videos(
        self,
        videos: list[dict[str, Any]],
        topic: str | None = None,
        learner_level: str = "beginner",
        preferred_language: str = "en",
        knowledge: dict[str, float] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        level = str(
            learner_level or "beginner"
        ).strip().casefold()

        if level not in self.VALID_LEVELS:
            level = "beginner"

        try:
            profile = personalization_service.build_profile(
                learner_level=level,
                preferred_language=preferred_language,
                knowledge=knowledge or {},
                history=history or [],
            )
        except Exception:
            profile = None

        ranked = []
        seen_ids = set()

        for video in videos or []:
            if not isinstance(video, dict):
                continue

            video_id = str(
                video.get("video_id") or video.get("id") or ""
            ).strip()

            if not video_id or video_id in seen_ids:
                continue

            topic_score = self._topic_relevance(video, topic)

            if topic and topic_score < 0.20:
                continue

            level_verified = self.matches_level(video, level)
            engagement = self._engagement_score(video)
            is_project = self._is_project_description(video)

            try:
                user_match = (
                    personalization_service.match_video(video, profile)
                    if profile is not None
                    else 0.0
                )
            except Exception:
                user_match = 0.0

            user_match = self._safe_float(user_match)

            score = (
                topic_score * 0.65
                + engagement * 0.15
                + user_match * 0.10
                + (0.05 if video.get("is_indian_creator") else 0.0)
                + (0.05 if is_project else 0.0)
            )

            ranked.append({
                **video,
                "video_id": video_id,
                "difficulty": level,
                "level_verified": level_verified,
                "level_match": (
                    "verified" if level_verified else "unverified"
                ),
                "is_project_related": is_project,
                "topic_relevance": round(topic_score, 4),
                "engagement_score": round(engagement, 4),
                "user_match": round(user_match, 4),
                "recommendation_score": round(
                    max(0.0, min(score, 1.0)),
                    4,
                ),
                "reason": self._build_reason(
                    video,
                    level,
                    preferred_language,
                    level_verified,
                ),
            })

            seen_ids.add(video_id)

        ranked.sort(
            key=lambda item: (
                item["level_verified"],
                item["topic_relevance"],
                item["recommendation_score"],
                self._safe_int(item.get("views")),
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
        level = str(level or "beginner").strip().casefold()

        if level not in self.VALID_LEVELS or limit <= 0:
            return []

        used_video_ids = used_video_ids or set()
        selected = []
        seen_ids = set()
        seen_titles = set()

        for video in videos or []:
            if not isinstance(video, dict):
                continue

            video_id = str(
                video.get("video_id") or video.get("id") or ""
            ).strip()

            if not video_id:
                continue

            title = self._normalize_title(
                str(video.get("title") or "")
            )

            if video_id in used_video_ids or video_id in seen_ids:
                continue

            if title and title in seen_titles:
                continue

            verified = bool(
                video.get(
                    "level_verified",
                    video.get("levelVerified", False),
                )
            )

            selected.append({
                **video,
                "video_id": video_id,
                "difficulty": level,
                "level_verified": verified,
                "level_match": (
                    "verified" if verified else "unverified"
                ),
                "is_project_related": self._is_project_description(video),
            })

            seen_ids.add(video_id)

            if title:
                seen_titles.add(title)

            if len(selected) >= limit:
                break

        return selected

    @classmethod
    def _is_project_description(
        cls,
        video: dict[str, Any],
    ) -> bool:
        text = cls._text(video)
        return any(
            cls._contains_phrase(text, phrase)
            for phrase in cls.PROJECT_KEYWORDS
        )

    @staticmethod
    def _engagement_score(
        video: dict[str, Any],
    ) -> float:
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
            re.sub(r"[^\w\s]", "", str(title).casefold()).split()
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

    @classmethod
    def _build_reason(
        cls,
        video: dict[str, Any],
        level: str,
        language: str,
        level_verified: bool = False,
    ) -> str:
        if level_verified:
            reasons = [
                f"content explicitly identifies {level} material"
            ]
        else:
            reasons = [
                f"topic is relevant; {level} suitability is unverified"
            ]

        if cls._is_project_description(video):
            reasons.append("project-related content")

        if video.get("is_indian_creator"):
            reasons.append("Indian creator")

        if cls._safe_int(video.get("views")) > 0:
            reasons.append("view-count popularity")

        return "Recommended because " + ", ".join(reasons) + "."


recommendation_service = RecommendationService()




