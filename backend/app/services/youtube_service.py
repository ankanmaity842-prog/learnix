from typing import Any

import httpx

from app.config import settings
from app.core.cache import cache


YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"


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

        cache_key = (
            f"youtube:{query}:{limit}:{language}"
        )

        cached = cache.get(cache_key)

        if cached is not None:
            return cached

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": limit,
            "relevanceLanguage": language,
            "key": settings.YOUTUBE_API_KEY,
        }

        async with httpx.AsyncClient(
            timeout=15
        ) as client:
            response = await client.get(
                YOUTUBE_SEARCH_URL,
                params=params,
            )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get(
                "id",
                {},
            ).get("videoId")

            if not video_id:
                continue

            thumbnails = snippet.get(
                "thumbnails",
                {},
            )

            thumbnail = (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url")
                or ""
            )

            results.append(
                {
                    "video_id": video_id,
                    "title": snippet.get(
                        "title",
                        "",
                    ),
                    "description": snippet.get(
                        "description",
                        "",
                    ),
                    "channel": snippet.get(
                        "channelTitle",
                        "",
                    ),
                    "thumbnail": thumbnail,
                    "published_at": snippet.get(
                        "publishedAt",
                        "",
                    ),
                    "language": language,
                }
            )

        cache.set(
            cache_key,
            results,
            ttl=300,
        )

        return results

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
            "part": (
                "snippet,"
                "contentDetails,"
                "statistics"
            ),
            "id": video_id,
            "key": settings.YOUTUBE_API_KEY,
        }

        async with httpx.AsyncClient(
            timeout=15
        ) as client:
            response = await client.get(
                YOUTUBE_VIDEO_URL,
                params=params,
            )

        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            return None

        item = items[0]

        snippet = item.get(
            "snippet",
            {},
        )

        content = item.get(
            "contentDetails",
            {},
        )

        statistics = item.get(
            "statistics",
            {},
        )

        result = {
            "video_id": video_id,
            "title": snippet.get(
                "title",
                "",
            ),
            "description": snippet.get(
                "description",
                "",
            ),
            "channel": snippet.get(
                "channelTitle",
                "",
            ),
            "thumbnail": (
                snippet.get(
                    "thumbnails",
                    {},
                )
                .get(
                    "high",
                    {},
                )
                .get(
                    "url",
                    "",
                )
            ),
            "published_at": snippet.get(
                "publishedAt",
                "",
            ),
            "duration": content.get(
                "duration",
                "",
            ),
            "views": self._safe_int(
                statistics.get(
                    "viewCount",
                    0,
                )
            ),
            "likes": self._safe_int(
                statistics.get(
                    "likeCount",
                    0,
                )
            ),
        }

        cache.set(
            cache_key,
            result,
            ttl=600,
        )

        return result

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0


youtube_service = YouTubeService()