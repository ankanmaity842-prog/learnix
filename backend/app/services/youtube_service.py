from typing import Any

import httpx

from app.config import settings
from app.core.cache import cache


YOUTUBE_SEARCH_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)

YOUTUBE_VIDEO_URL = (
    "https://www.googleapis.com/youtube/v3/videos"
)

YOUTUBE_CHANNEL_URL = (
    "https://www.googleapis.com/youtube/v3/channels"
)


class YouTubeService:
    """
    YouTube discovery service.

    Responsibilities:
    - Educational video search
    - Pagination
    - View-based discovery
    - Channel discovery
    - Channel country detection
    - Video statistics
    - Language-oriented search
    """

    EDUCATIONAL_TERMS = (
        "tutorial",
        "course",
        "lecture",
        "lesson",
        "explained",
        "education",
        "educational",
        "learn",
        "learning",
        "class",
        "programming",
        "concept",
        "guide",
        "study",
        "exam",
        "training",
        "how to",
    )

    ENTERTAINMENT_TERMS = (
        "movie",
        "movies",
        "song",
        "songs",
        "music",
        "comedy",
        "funny",
        "roast",
        "reaction",
        "vlog",
        "vlogging",
        "shorts",
        "meme",
        "memes",
        "trailer",
        "web series",
        "serial",
        "celebrity",
        "dance",
        "prank",
        "entertainment",
        "gaming",
        "gameplay",
        "stream",
        "live stream",
        "podcast",
    )

    HINDI_TERMS = (
        "hindi",
        "हिंदी",
        "हिन्दी",
    )

    BENGALI_TERMS = (
        "bengali",
        "bangla",
        "বাংলা",
        "বাঙালি",
        "বাংলায়",
        "বাংলাতে",
    )

    async def search_videos(
        self,
        query: str,
        limit: int = 50,
        language: str = "en",
        max_pages: int = 3,
        educational_only: bool = True,
    ) -> list[dict[str, Any]]:

        query = query.strip()

        if not query:
            return []

        limit = max(1, min(limit, 50))
        max_pages = max(1, min(max_pages, 10))

        cache_key = (
            f"youtube:search:"
            f"{query}:"
            f"{limit}:"
            f"{language}:"
            f"{max_pages}:"
            f"{educational_only}"
        )

        cached = cache.get(cache_key)

        if cached is not None:
            return cached

        results: list[dict[str, Any]] = []
        page_token: str | None = None

        for _ in range(max_pages):
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": limit,
                "order": "viewCount",
                "relevanceLanguage": language,
                "safeSearch": "strict",
                "key": settings.YOUTUBE_API_KEY,
            }

            if language in {"hi", "bn"}:
                params["regionCode"] = "IN"

            if page_token:
                params["pageToken"] = page_token

            async with httpx.AsyncClient(
                timeout=20
            ) as client:

                response = await client.get(
                    YOUTUBE_SEARCH_URL,
                    params=params,
                )

            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                video_id = (
                    item.get("id", {})
                    .get("videoId")
                )

                if not video_id:
                    continue

                title = snippet.get(
                    "title",
                    "",
                )

                description = snippet.get(
                    "description",
                    "",
                )

                channel = snippet.get(
                    "channelTitle",
                    "",
                )

                combined_text = (
                    f"{title} "
                    f"{description} "
                    f"{channel}"
                )

                if (
                    educational_only
                    and self.is_entertainment(
                        combined_text
                    )
                ):
                    continue

                results.append(
                    {
                        "video_id": video_id,
                        "title": title,
                        "description": description,
                        "channel": channel,
                        "channel_id": snippet.get(
                            "channelId",
                            "",
                        ),
                        "thumbnail": self._thumbnail(
                            snippet
                        ),
                        "published_at": snippet.get(
                            "publishedAt",
                            "",
                        ),
                        "language": language,
                        "views": 0,
                        "likes": 0,
                        "duration": "",
                        "channel_country": "",
                        "is_indian_creator": False,
                        "is_language_creator": False,
                    }
                )

            page_token = data.get(
                "nextPageToken"
            )

            if not page_token:
                break

        unique = {}

        for video in results:
            unique[
                video["video_id"]
            ] = video

        final_results = list(
            unique.values()
        )

        cache.set(
            cache_key,
            final_results,
            ttl=300,
        )

        return final_results

    async def enrich_search_results(
        self,
        videos: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not videos:
            return []

        video_ids = list(
            dict.fromkeys(
                video.get("video_id")
                for video in videos
                if video.get("video_id")
            )
        )

        channel_ids = list(
            dict.fromkeys(
                video.get("channel_id")
                for video in videos
                if video.get("channel_id")
            )
        )

        video_details: dict[
            str,
            dict[str, Any]
        ] = {}

        channel_details: dict[
            str,
            dict[str, Any]
        ] = {}

        async with httpx.AsyncClient(
            timeout=25
        ) as client:

            # YouTube allows up to 50 IDs per request.
            for start in range(
                0,
                len(video_ids),
                50,
            ):
                batch = video_ids[
                    start:start + 50
                ]

                response = await client.get(
                    YOUTUBE_VIDEO_URL,
                    params={
                        "part": (
                            "snippet,"
                            "contentDetails,"
                            "statistics"
                        ),
                        "id": ",".join(batch),
                        "key": settings.YOUTUBE_API_KEY,
                    },
                )

                response.raise_for_status()

                for item in response.json().get(
                    "items",
                    [],
                ):
                    video_id = item.get(
                        "id"
                    )

                    snippet = item.get(
                        "snippet",
                        {},
                    )

                    statistics = item.get(
                        "statistics",
                        {},
                    )

                    content = item.get(
                        "contentDetails",
                        {},
                    )

                    video_details[
                        video_id
                    ] = {
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
                        "channel_id": snippet.get(
                            "channelId",
                            "",
                        ),
                        "thumbnail": self._thumbnail(
                            snippet
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

            for start in range(
                0,
                len(channel_ids),
                50,
            ):
                batch = channel_ids[
                    start:start + 50
                ]

                response = await client.get(
                    YOUTUBE_CHANNEL_URL,
                    params={
                        "part": (
                            "snippet,"
                            "statistics"
                        ),
                        "id": ",".join(batch),
                        "key": settings.YOUTUBE_API_KEY,
                    },
                )

                response.raise_for_status()

                for item in response.json().get(
                    "items",
                    [],
                ):
                    channel_id = item.get(
                        "id"
                    )

                    snippet = item.get(
                        "snippet",
                        {},
                    )

                    statistics = item.get(
                        "statistics",
                        {},
                    )

                    channel_details[
                        channel_id
                    ] = {
                        "channel_country": (
                            snippet.get(
                                "country",
                                "",
                            )
                        ),
                        "channel_title": (
                            snippet.get(
                                "title",
                                "",
                            )
                        ),
                        "channel_description": (
                            snippet.get(
                                "description",
                                "",
                            )
                        ),
                        "subscriber_count": (
                            self._safe_int(
                                statistics.get(
                                    "subscriberCount",
                                    0,
                                )
                            )
                        ),
                    }

        enriched = []

        for video in videos:
            video_id = video.get(
                "video_id"
            )

            details = video_details.get(
                video_id,
                {},
            )

            channel_id = details.get(
                "channel_id",
                video.get(
                    "channel_id",
                    "",
                ),
            )

            channel = channel_details.get(
                channel_id,
                {},
            )

            country = channel.get(
                "channel_country",
                "",
            )

            channel_text = " ".join(
                [
                    str(
                        details.get(
                            "channel",
                            "",
                        )
                    ),
                    str(
                        channel.get(
                            "channel_title",
                            "",
                        )
                    ),
                    str(
                        channel.get(
                            "channel_description",
                            "",
                        )
                    ),
                ]
            )

            video_text = " ".join(
                [
                    str(
                        details.get(
                            "title",
                            "",
                        )
                    ),
                    str(
                        details.get(
                            "description",
                            "",
                        )
                    ),
                ]
            )

            language_creator = (
                self.is_language_creator(
                    video_text=video_text,
                    channel_text=channel_text,
                    language=video.get(
                        "language",
                        "en",
                    ),
                )
            )

            enriched.append(
                {
                    **video,
                    **details,
                    "channel_country": country,
                    "subscriber_count": channel.get(
                        "subscriber_count",
                        0,
                    ),
                    "is_indian_creator": (
                        country == "IN"
                    ),
                    "is_language_creator": (
                        language_creator
                    ),
                }
            )

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

        limit = max(
            1,
            min(limit, 50),
        )

        params = {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": limit,
            "order": "relevance",
            "relevanceLanguage": language,
            "regionCode": "IN",
            "safeSearch": "strict",
            "key": settings.YOUTUBE_API_KEY,
        }

        async with httpx.AsyncClient(
            timeout=20
        ) as client:

            response = await client.get(
                YOUTUBE_SEARCH_URL,
                params=params,
            )

        response.raise_for_status()

        data = response.json()

        channels = []

        for item in data.get(
            "items",
            [],
        ):
            snippet = item.get(
                "snippet",
                {},
            )

            channel_id = (
                item.get("id", {})
                .get("channelId")
            )

            if not channel_id:
                continue

            channels.append(
                {
                    "channel_id": channel_id,
                    "channel": snippet.get(
                        "title",
                        "",
                    ),
                    "description": snippet.get(
                        "description",
                        "",
                    ),
                    "thumbnail": self._thumbnail(
                        snippet
                    ),
                    "language": language,
                }
            )

        return channels

    async def get_video(
        self,
        video_id: str,
    ) -> dict[str, Any] | None:

        video_id = video_id.strip()

        if not video_id:
            return None

        cache_key = (
            f"youtube:video:{video_id}"
        )

        cached = cache.get(
            cache_key
        )

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

        items = response.json().get(
            "items",
            [],
        )

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
            "channel_id": snippet.get(
                "channelId",
                "",
            ),
            "thumbnail": self._thumbnail(
                snippet
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

    @classmethod
    def is_entertainment(
        cls,
        text: str,
    ) -> bool:

        text = text.lower()

        return any(
            term in text
            for term in cls.ENTERTAINMENT_TERMS
        )

    @classmethod
    def is_language_creator(
        cls,
        video_text: str,
        channel_text: str,
        language: str,
    ) -> bool:

        combined = (
            f"{video_text} "
            f"{channel_text}"
        ).lower()

        if language == "hi":
            return any(
                term.lower() in combined
                for term in cls.HINDI_TERMS
            )

        if language == "bn":
            return any(
                term.lower() in combined
                for term in cls.BENGALI_TERMS
            )

        return True

    @staticmethod
    def _thumbnail(
        snippet: dict[str, Any],
    ) -> str:

        thumbnails = snippet.get(
            "thumbnails",
            {},
        )

        return (
            thumbnails.get(
                "maxres",
                {},
            ).get(
                "url"
            )
            or thumbnails.get(
                "high",
                {},
            ).get(
                "url"
            )
            or thumbnails.get(
                "medium",
                {},
            ).get(
                "url"
            )
            or thumbnails.get(
                "default",
                {},
            ).get(
                "url"
            )
            or ""
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


youtube_service = YouTubeService()