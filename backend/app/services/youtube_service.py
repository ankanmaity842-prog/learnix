from typing import Any

import httpx

from app.config import settings
from app.core.cache import cache


YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"


class YouTubeService:
    async def search_videos(
        self,
        query: str,
        limit: int = 10,
        language: str = "en",
        max_results: int | None = None,
    ) -> list[dict[str, Any]]:
        if max_results is not None:
            limit = max_results

        limit = max(1, min(limit, 50))
        query = query.strip()

        if not query:
            return []

        cache_key = f"youtube:{query}:{limit}:{language}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": limit,
            "relevanceLanguage": language,
            "order": "viewCount",
            "key": settings.YOUTUBE_API_KEY,
        }

        if language in {"hi", "bn"}:
            params["regionCode"] = "IN"

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(YOUTUBE_SEARCH_URL, params=params)

        response.raise_for_status()
        data = response.json()
        results = []

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue

            thumbnails = snippet.get("thumbnails", {})
            results.append({
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "thumbnail": (
                    thumbnails.get("high", {}).get("url")
                    or thumbnails.get("medium", {}).get("url")
                    or thumbnails.get("default", {}).get("url")
                    or ""
                ),
                "published_at": snippet.get("publishedAt", ""),
                "language": language,
                "views": 0,
                "likes": 0,
                "channel_country": "",
                "is_indian_creator": False,
                "thumbnail_has_bengali": False,
            })

        cache.set(cache_key, results, ttl=300)
        return results

    async def enrich_search_results(
        self,
        videos: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not videos:
            return []

        video_ids = list(dict.fromkeys(
            video.get("video_id")
            for video in videos
            if video.get("video_id")
        ))
        channel_ids = list(dict.fromkeys(
            video.get("channel_id")
            for video in videos
            if video.get("channel_id")
        ))

        video_details: dict[str, dict[str, Any]] = {}
        channel_countries: dict[str, str] = {}

        async with httpx.AsyncClient(timeout=20) as client:
            for start in range(0, len(video_ids), 50):
                batch = video_ids[start:start + 50]
                response = await client.get(
                    YOUTUBE_VIDEO_URL,
                    params={
                        "part": "snippet,contentDetails,statistics",
                        "id": ",".join(batch),
                        "key": settings.YOUTUBE_API_KEY,
                    },
                )
                response.raise_for_status()

                for item in response.json().get("items", []):
                    video_id = item.get("id")
                    snippet = item.get("snippet", {})
                    statistics = item.get("statistics", {})
                    content = item.get("contentDetails", {})
                    thumbnails = snippet.get("thumbnails", {})

                    video_details[video_id] = {
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "channel": snippet.get("channelTitle", ""),
                        "channel_id": snippet.get("channelId", ""),
                        "thumbnail": (
                            thumbnails.get("high", {}).get("url")
                            or thumbnails.get("medium", {}).get("url")
                            or thumbnails.get("default", {}).get("url")
                            or ""
                        ),
                        "published_at": snippet.get("publishedAt", ""),
                        "duration": content.get("duration", ""),
                        "views": self._safe_int(
                            statistics.get("viewCount", 0)
                        ),
                        "likes": self._safe_int(
                            statistics.get("likeCount", 0)
                        ),
                    }

            for start in range(0, len(channel_ids), 50):
                batch = channel_ids[start:start + 50]
                response = await client.get(
                    YOUTUBE_CHANNEL_URL,
                    params={
                        "part": "snippet",
                        "id": ",".join(batch),
                        "key": settings.YOUTUBE_API_KEY,
                    },
                )
                response.raise_for_status()

                for item in response.json().get("items", []):
                    channel_countries[item["id"]] = (
                        item.get("snippet", {}).get("country", "")
                    )

        enriched = []
        for video in videos:
            details = video_details.get(video.get("video_id"), {})
            channel_id = details.get(
                "channel_id",
                video.get("channel_id", ""),
            )
            country = channel_countries.get(channel_id, "")

            enriched.append({
                **video,
                **details,
                "channel_country": country,
                "is_indian_creator": country == "IN",
                "thumbnail_has_bengali": video.get(
                    "thumbnail_has_bengali",
                    False,
                ),
            })

        return enriched

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

        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": settings.YOUTUBE_API_KEY,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(YOUTUBE_VIDEO_URL, params=params)

        response.raise_for_status()
        items = response.json().get("items", [])
        if not items:
            return None

        item = items[0]
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        statistics = item.get("statistics", {})
        thumbnails = snippet.get("thumbnails", {})

        result = {
            "video_id": video_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channel": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "thumbnail": (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url")
                or ""
            ),
            "published_at": snippet.get("publishedAt", ""),
            "duration": content.get("duration", ""),
            "views": self._safe_int(statistics.get("viewCount", 0)),
            "likes": self._safe_int(statistics.get("likeCount", 0)),
        }

        cache.set(cache_key, result, ttl=600)
        return result

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0


youtube_service = YouTubeService()