from difflib import SequenceMatcher
from typing import Any

import httpx

from app.config import settings
from app.core.cache import cache


YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"


class YouTubeService:
    EDUCATIONAL_TERMS = (
        "tutorial", "course", "lecture", "lesson", "explained",
        "education", "educational", "learn", "learning", "class",
        "programming", "concept", "guide", "study", "exam",
        "training", "how to", "fundamentals", "basics",
    )

    ENTERTAINMENT_TERMS = (
        "movie", "movies", "song", "songs", "music video",
        "comedy", "funny", "roast", "reaction", "vlog",
        "vlogging", "meme", "memes", "trailer", "web series",
        "serial", "celebrity", "dance", "prank", "entertainment",
        "gaming", "gameplay", "stream", "live stream",
    )

    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY

    async def search_videos(
        self,
        query: str,
        limit: int = 50,
        language: str = "en",
        max_pages: int = 2,
        educational_only: bool = True,
        channel_id: str | None = None,
    ) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            return []

        limit = max(1, min(limit, 50))
        max_pages = max(1, min(max_pages, 5))

        cache_key = (
            f"youtube:search:{query}:{limit}:{language}:"
            f"{max_pages}:{educational_only}:{channel_id or ''}"
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        results: list[dict[str, Any]] = []
        page_token = None

        async with httpx.AsyncClient(timeout=20) as client:
            for _ in range(max_pages):
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": limit,
                    "order": "viewCount",
                    "relevanceLanguage": language,
                    "safeSearch": "strict",
                    "key": self.api_key,
                }

                if language in {"hi", "bn"}:
                    params["regionCode"] = "IN"

                if channel_id:
                    params["channelId"] = channel_id

                if page_token:
                    params["pageToken"] = page_token

                response = await client.get(
                    YOUTUBE_SEARCH_URL,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    video_id = item.get("id", {}).get("videoId")
                    if not video_id:
                        continue

                    title = snippet.get("title", "")
                    description = snippet.get("description", "")
                    channel = snippet.get("channelTitle", "")

                    if educational_only and self.is_entertainment(
                        f"{title} {description}"
                    ):
                        continue

                    results.append({
                        "video_id": video_id,
                        "title": title,
                        "description": description,
                        "channel": channel,
                        "channel_id": snippet.get("channelId", ""),
                        "thumbnail": self._thumbnail(snippet),
                        "published_at": snippet.get("publishedAt", ""),
                        "language": language,
                        "views": 0,
                        "likes": 0,
                        "duration": "",
                        "channel_country": "",
                        "subscriber_count": 0,
                        "is_indian_creator": False,
                        # Do not claim a language is verified from
                        # a channel name or description.
                        "is_language_creator": language == "en",
                        "language_verified": language == "en",
                    })

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

        unique = {}
        for video in results:
            unique[video["video_id"]] = video

        final_results = list(unique.values())
        cache.set(cache_key, final_results, ttl=300)
        return final_results

    async def enrich_search_results(
        self,
        videos: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not videos:
            return []

        video_ids = list(dict.fromkeys(
            v.get("video_id") for v in videos if v.get("video_id")
        ))
        channel_ids = list(dict.fromkeys(
            v.get("channel_id") for v in videos if v.get("channel_id")
        ))

        video_details: dict[str, dict[str, Any]] = {}
        channel_details: dict[str, dict[str, Any]] = {}

        async with httpx.AsyncClient(timeout=25) as client:
            for start in range(0, len(video_ids), 50):
                response = await client.get(
                    YOUTUBE_VIDEO_URL,
                    params={
                        "part": "snippet,contentDetails,statistics",
                        "id": ",".join(video_ids[start:start + 50]),
                        "key": self.api_key,
                    },
                )
                response.raise_for_status()

                for item in response.json().get("items", []):
                    video_id = item.get("id")
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    content = item.get("contentDetails", {})

                    video_details[video_id] = {
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "channel": snippet.get("channelTitle", ""),
                        "channel_id": snippet.get("channelId", ""),
                        "thumbnail": self._thumbnail(snippet),
                        "published_at": snippet.get("publishedAt", ""),
                        "duration": content.get("duration", ""),
                        "views": self._safe_int(stats.get("viewCount")),
                        "likes": self._safe_int(stats.get("likeCount")),
                    }

            for start in range(0, len(channel_ids), 50):
                response = await client.get(
                    YOUTUBE_CHANNEL_URL,
                    params={
                        "part": "snippet,statistics",
                        "id": ",".join(channel_ids[start:start + 50]),
                        "key": self.api_key,
                    },
                )
                response.raise_for_status()

                for item in response.json().get("items", []):
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    channel_details[item["id"]] = {
                        "channel_country": snippet.get("country", ""),
                        "channel_title": snippet.get("title", ""),
                        "channel_description": snippet.get("description", ""),
                        "subscriber_count": self._safe_int(
                            stats.get("subscriberCount")
                        ),
                    }

        enriched = []
        for video in videos:
            video_id = video.get("video_id")
            details = video_details.get(video_id, {})
            channel_id = details.get(
                "channel_id", video.get("channel_id", "")
            )
            channel = channel_details.get(channel_id, {})
            country = channel.get("channel_country", "")

            enriched.append({
                **video,
                **details,
                **channel,
                "channel_country": country,
                "is_indian_creator": country == "IN",
            })

        return enriched

    async def search_channels(
        self,
        query: str,
        language: str = "en",
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            return []

        limit = max(1, min(limit, 50))
        cache_key = f"youtube:channels:{query}:{language}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                YOUTUBE_SEARCH_URL,
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "channel",
                    "maxResults": limit,
                    "order": "relevance",
                    "relevanceLanguage": language,
                    "regionCode": "IN",
                    "safeSearch": "strict",
                    "key": self.api_key,
                },
            )
            response.raise_for_status()
            data = response.json()

        channels = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            channel_id = item.get("id", {}).get("channelId")
            if not channel_id:
                continue

            channels.append({
                "channel_id": channel_id,
                "channel": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "thumbnail": self._thumbnail(snippet),
                "language": language,
                "match_score": round(
                    SequenceMatcher(
                        None,
                        query.casefold(),
                        snippet.get("title", "").casefold(),
                    ).ratio(),
                    3,
                ),
            })

        channels.sort(key=lambda x: x["match_score"], reverse=True)
        cache.set(cache_key, channels, ttl=600)
        return channels

    async def get_video(
        self,
        video_id: str,
    ) -> dict[str, Any] | None:
        video_id = video_id.strip()
        if not video_id:
            return None

        cache_key = f"youtube:video:{video_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                YOUTUBE_VIDEO_URL,
                params={
                    "part": "snippet,contentDetails,statistics",
                    "id": video_id,
                    "key": self.api_key,
                },
            )
            response.raise_for_status()
            items = response.json().get("items", [])

        if not items:
            return None

        item = items[0]
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        stats = item.get("statistics", {})

        result = {
            "video_id": video_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channel": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "thumbnail": self._thumbnail(snippet),
            "published_at": snippet.get("publishedAt", ""),
            "duration": content.get("duration", ""),
            "views": self._safe_int(stats.get("viewCount")),
            "likes": self._safe_int(stats.get("likeCount")),
        }
        cache.set(cache_key, result, ttl=600)
        return result

    @classmethod
    def is_entertainment(cls, text: str) -> bool:
        text = text.casefold()
        return any(term in text for term in cls.ENTERTAINMENT_TERMS)

    @staticmethod
    def _thumbnail(snippet: dict[str, Any]) -> str:
        thumbnails = snippet.get("thumbnails", {})
        for size in ("maxres", "high", "medium", "default"):
            url = thumbnails.get(size, {}).get("url")
            if url:
                return url
        return ""

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0


youtube_service = YouTubeService()