import logging
from difflib import SequenceMatcher
from typing import Any

import httpx

from app.config import settings
from app.core.cache import cache

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"


class YouTubeService:
    ENTERTAINMENT_TITLE_TERMS = (
        "official music video",
        "full movie",
        "movie trailer",
        "official trailer",
        "comedy sketch",
        "stand up comedy",
        "roast video",
        "celebrity gossip",
        "prank video",
        "funny compilation",
        "reaction video",
        "dance performance",
        "web series episode",
    )

    VALID_LEVELS = {"beginner", "intermediate", "advanced"}

    # Successful results are cached to avoid repeating identical searches.
    SEARCH_CACHE_TTL = 3600
    CHANNEL_CACHE_TTL = 3600
    DETAIL_CACHE_TTL = 1800

    # Short circuit repeated searches after a quota error.
    # This is a temporary circuit breaker, not an exact Google quota reset.
    SEARCH_QUOTA_KEY = "youtube:search:quota_exhausted:v1"
    SEARCH_QUOTA_TTL = 3600

    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY

    @staticmethod
    def _is_search_quota_error(
        status_code: int,
        reason: str,
        message: str,
    ) -> bool:
        text = f"{reason} {message}".casefold().replace("_", "")

        return status_code in (403, 429) and any(
            marker in text
            for marker in (
                "quotaexceeded",
                "ratelimitexceeded",
                "quota exceeded",
                "daily limit",
                "search queries per day",
            )
        )

    @staticmethod
    def _extract_api_error(
        response: httpx.Response,
    ) -> tuple[str, str]:
        reason = "unknown"
        message = response.text[:300]

        try:
            error_data = response.json().get("error", {})
            errors = error_data.get("errors", [])

            if errors:
                reason = str(errors[0].get("reason", "unknown"))
            else:
                reason = str(error_data.get("status", "unknown"))

            message = str(error_data.get("message", message))
        except (ValueError, TypeError, AttributeError):
            pass

        return reason, message

    def is_search_quota_exhausted(self) -> bool:
        """Return whether the temporary quota circuit breaker is active."""
        try:
            return bool(cache.get(self.SEARCH_QUOTA_KEY))
        except Exception:
            logger.exception("Could not read YouTube quota state")
            return False

    def _mark_search_quota_exhausted(self) -> None:
        try:
            cache.set(
                self.SEARCH_QUOTA_KEY,
                True,
                ttl=self.SEARCH_QUOTA_TTL,
            )
        except Exception:
            logger.exception("Could not store YouTube quota state")

    async def search_videos(
        self,
        query: str,
        limit: int = 50,
        language: str = "en",
        max_pages: int = 1,
        educational_only: bool = True,
        channel_id: str | None = None,
        level: str | None = None,
    ) -> list[dict[str, Any]]:
        query = str(query or "").strip()
        language = str(language or "en").strip().lower()
        channel_id = str(channel_id or "").strip() or None

        if not query:
            logger.warning("YouTube search skipped: empty query")
            return []

        if language not in {"en", "hi", "bn"}:
            language = "en"

        if level is not None:
            level = str(level).strip().casefold()
            if level not in self.VALID_LEVELS:
                raise ValueError(
                    "level must be beginner, intermediate, or advanced"
                )

        limit = max(1, min(int(limit), 50))
        max_pages = max(1, min(int(max_pages), 5))

        cache_key = (
            f"youtube:search:v5:{query.casefold()}:{limit}:{language}:"
            f"{max_pages}:{educational_only}:"
            f"{channel_id or 'all'}:{level or 'all'}"
        )

        try:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.info(
                    "YouTube search cache hit: query=%r count=%d",
                    query,
                    len(cached),
                )
                return cached
        except Exception:
            logger.exception("YouTube search cache read failed")

        # Check cache first so previously fetched results can still be used
        # while the live search quota is exhausted.
        if self.is_search_quota_exhausted():
            logger.warning(
                "YouTube search skipped: quota circuit breaker active; "
                "query=%r",
                query,
            )
            return []

        if not self.api_key:
            logger.error("YOUTUBE_API_KEY is not configured")
            return []

        logger.info(
            "YouTube search starting: query=%r language=%s "
            "limit=%d pages=%d channel_filter=%s",
            query,
            language,
            limit,
            max_pages,
            channel_id or "none",
        )

        results: list[dict[str, Any]] = []
        page_token = None
        failed = False

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                for page_number in range(max_pages):
                    params: dict[str, Any] = {
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": limit,
                        "order": "relevance",
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

                    try:
                        response = await client.get(
                            YOUTUBE_SEARCH_URL,
                            params=params,
                        )
                        response.raise_for_status()
                        data = response.json()

                    except httpx.HTTPStatusError as exc:
                        reason, message = self._extract_api_error(
                            exc.response
                        )

                        logger.error(
                            "YouTube search failed: status=%s "
                            "reason=%s query=%r message=%s",
                            exc.response.status_code,
                            reason,
                            query,
                            message,
                        )

                        if self._is_search_quota_error(
                            exc.response.status_code,
                            reason,
                            message,
                        ):
                            self._mark_search_quota_exhausted()

                        failed = True
                        break

                    except httpx.RequestError:
                        logger.exception(
                            "YouTube network error: query=%r",
                            query,
                        )
                        failed = True
                        break

                    items = data.get("items", [])

                    logger.info(
                        "YouTube API response: query=%r page=%d items=%d",
                        query,
                        page_number + 1,
                        len(items),
                    )

                    for item in items:
                        snippet = item.get("snippet") or {}
                        item_id = item.get("id") or {}
                        video_id = item_id.get("videoId")

                        if not video_id:
                            continue

                        title = str(snippet.get("title") or "")
                        description = str(
                            snippet.get("description") or ""
                        )

                        if (
                            educational_only
                            and self.is_entertainment_title(title)
                        ):
                            continue

                        result_channel_id = str(
                            snippet.get("channelId")
                            or item_id.get("channelId")
                            or ""
                        ).strip()

                        if (
                            channel_id
                            and result_channel_id != channel_id
                        ):
                            continue

                        results.append({
                            "video_id": str(video_id),
                            "title": title,
                            "description": description,
                            "channel": str(
                                snippet.get("channelTitle") or ""
                            ),
                            "channel_id": result_channel_id,
                            "thumbnail": self._thumbnail(snippet),
                            "published_at": str(
                                snippet.get("publishedAt") or ""
                            ),
                            "language": language,
                            "views": 0,
                            "likes": 0,
                            "duration": "",
                            "channel_country": "",
                            "subscriber_count": 0,
                            "is_indian_creator": False,
                            "is_language_creator": False,
                            "language_verified": False,
                        })

                    page_token = data.get("nextPageToken")
                    if not page_token:
                        break

        except Exception:
            failed = True
            logger.exception(
                "Unexpected YouTube search exception: query=%r",
                query,
            )

        unique: dict[str, dict[str, Any]] = {}
        for video in results:
            unique[video["video_id"]] = video

        final_results = list(unique.values())

        logger.info(
            "YouTube search finished: query=%r candidates=%d failed=%s",
            query,
            len(final_results),
            failed,
        )

        # Never cache a failed response as a successful search.
        if not failed and final_results:
            try:
                cache.set(
                    cache_key,
                    final_results,
                    ttl=self.SEARCH_CACHE_TTL,
                )
            except Exception:
                logger.exception("YouTube search cache write failed")

        return final_results

    async def enrich_search_results(
        self,
        videos: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not videos:
            return []

        if not self.api_key:
            logger.error(
                "YOUTUBE_API_KEY is not configured during enrichment"
            )
            return videos

        video_ids = list(dict.fromkeys(
            str(video.get("video_id") or video.get("id") or "").strip()
            for video in videos
            if video.get("video_id") or video.get("id")
        ))

        channel_ids = list(dict.fromkeys(
            str(video.get("channel_id") or "").strip()
            for video in videos
            if video.get("channel_id")
        ))

        video_details: dict[str, dict[str, Any]] = {}
        channel_details: dict[str, dict[str, Any]] = {}

        async with httpx.AsyncClient(timeout=25) as client:
            for start in range(0, len(video_ids), 50):
                batch = video_ids[start:start + 50]
                cache_key = "youtube:video_details:v2:" + ",".join(batch)

                try:
                    cached = cache.get(cache_key)
                    if cached is not None:
                        video_details.update(cached)
                        continue
                except Exception:
                    logger.exception("Video details cache read failed")

                try:
                    response = await client.get(
                        YOUTUBE_VIDEO_URL,
                        params={
                            "part": "snippet,contentDetails,statistics",
                            "id": ",".join(batch),
                            "key": self.api_key,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                except httpx.HTTPStatusError as exc:
                    reason, message = self._extract_api_error(exc.response)
                    logger.error(
                        "YouTube video details failed: HTTP %s "
                        "reason=%s message=%s",
                        exc.response.status_code,
                        reason,
                        message,
                    )
                    continue

                except httpx.RequestError:
                    logger.exception("YouTube video details network error")
                    continue

                batch_details = {}

                for item in data.get("items", []):
                    video_id = str(item.get("id") or "")
                    snippet = item.get("snippet") or {}
                    stats = item.get("statistics") or {}
                    content = item.get("contentDetails") or {}

                    batch_details[video_id] = {
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

                video_details.update(batch_details)

                if batch_details:
                    try:
                        cache.set(
                            cache_key,
                            batch_details,
                            ttl=self.DETAIL_CACHE_TTL,
                        )
                    except Exception:
                        logger.exception("Video details cache write failed")

            for start in range(0, len(channel_ids), 50):
                batch = channel_ids[start:start + 50]
                cache_key = "youtube:channel_details:v2:" + ",".join(batch)

                try:
                    cached = cache.get(cache_key)
                    if cached is not None:
                        channel_details.update(cached)
                        continue
                except Exception:
                    logger.exception("Channel details cache read failed")

                try:
                    response = await client.get(
                        YOUTUBE_CHANNEL_URL,
                        params={
                            "part": "snippet,statistics",
                            "id": ",".join(batch),
                            "key": self.api_key,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                except httpx.HTTPStatusError as exc:
                    reason, message = self._extract_api_error(exc.response)
                    logger.error(
                        "YouTube channel details failed: HTTP %s "
                        "reason=%s message=%s",
                        exc.response.status_code,
                        reason,
                        message,
                    )
                    continue

                except httpx.RequestError:
                    logger.exception(
                        "YouTube channel details network error"
                    )
                    continue

                batch_details = {}

                for item in data.get("items", []):
                    snippet = item.get("snippet") or {}
                    stats = item.get("statistics") or {}

                    batch_details[str(item.get("id") or "")] = {
                        "channel_country": snippet.get("country", ""),
                        "channel_title": snippet.get("title", ""),
                        "channel_description": snippet.get(
                            "description", ""
                        ),
                        "subscriber_count": self._safe_int(
                            stats.get("subscriberCount")
                        ),
                    }

                channel_details.update(batch_details)

                if batch_details:
                    try:
                        cache.set(
                            cache_key,
                            batch_details,
                            ttl=self.DETAIL_CACHE_TTL,
                        )
                    except Exception:
                        logger.exception("Channel details cache write failed")

        enriched = []

        for video in videos:
            video_id = str(
                video.get("video_id") or video.get("id") or ""
            ).strip()

            details = video_details.get(video_id, {})
            channel_id = str(
                details.get("channel_id")
                or video.get("channel_id")
                or ""
            ).strip()

            channel = channel_details.get(channel_id, {})

            enriched_video = {
                **video,
                **details,
                **channel,
                "video_id": video_id,
                "channel_id": channel_id,
                "channel_country": channel.get("channel_country", ""),
                "is_indian_creator": (
                    channel.get("channel_country", "").upper() == "IN"
                ),
            }

            enriched.append(enriched_video)

        logger.info(
            "YouTube enrichment completed: input=%d output=%d "
            "channel_ids=%d enriched_channels=%d",
            len(videos),
            len(enriched),
            len(channel_ids),
            len(channel_details),
        )

        return enriched

    async def search_channels(
        self,
        query: str,
        language: str = "en",
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        query = str(query or "").strip()
        language = str(language or "en").strip().lower()

        if not query:
            return []

        if language not in {"en", "hi", "bn"}:
            language = "en"

        limit = max(1, min(int(limit), 50))
        cache_key = f"youtube:channels:v4:{query.casefold()}:{language}:{limit}"

        try:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            logger.exception("YouTube channel cache read failed")

        if self.is_search_quota_exhausted():
            logger.warning(
                "YouTube channel search skipped: quota circuit breaker active"
            )
            return []

        if not self.api_key:
            logger.error("YOUTUBE_API_KEY is not configured")
            return []

        try:
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

        except httpx.HTTPStatusError as exc:
            reason, message = self._extract_api_error(exc.response)

            if self._is_search_quota_error(
                exc.response.status_code,
                reason,
                message,
            ):
                self._mark_search_quota_exhausted()

            logger.error(
                "YouTube channel search failed: HTTP %s "
                "reason=%s message=%s",
                exc.response.status_code,
                reason,
                message,
            )
            return []

        except httpx.RequestError:
            logger.exception("YouTube channel search network error")
            return []

        channels = []

        for item in data.get("items", []):
            snippet = item.get("snippet") or {}
            item_id = item.get("id") or {}
            channel_id = (
                item_id.get("channelId") or snippet.get("channelId")
            )

            if not channel_id:
                continue

            title = str(snippet.get("title") or "")

            channels.append({
                "channel_id": str(channel_id),
                "channel": title,
                "description": snippet.get("description", ""),
                "thumbnail": self._thumbnail(snippet),
                "language": language,
                "match_score": round(
                    SequenceMatcher(
                        None,
                        query.casefold(),
                        title.casefold(),
                    ).ratio(),
                    3,
                ),
            })

        channels.sort(
            key=lambda item: item["match_score"],
            reverse=True,
        )

        if channels:
            try:
                cache.set(
                    cache_key,
                    channels,
                    ttl=self.CHANNEL_CACHE_TTL,
                )
            except Exception:
                logger.exception("YouTube channel cache write failed")

        logger.info(
            "YouTube channel search query=%r results=%d",
            query,
            len(channels),
        )

        return channels

    async def get_video(
        self,
        video_id: str,
    ) -> dict[str, Any] | None:
        video_id = str(video_id or "").strip()

        if not video_id:
            return None

        cache_key = f"youtube:video:v4:{video_id}"

        try:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            logger.exception("YouTube video cache read failed")

        if not self.api_key:
            logger.error("YOUTUBE_API_KEY is not configured")
            return None

        try:
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

        except httpx.HTTPStatusError as exc:
            reason, message = self._extract_api_error(exc.response)
            logger.error(
                "YouTube video lookup failed: HTTP %s "
                "reason=%s message=%s",
                exc.response.status_code,
                reason,
                message,
            )
            return None

        except httpx.RequestError:
            logger.exception("YouTube video lookup network error")
            return None

        if not items:
            return None

        item = items[0]
        snippet = item.get("snippet") or {}
        content = item.get("contentDetails") or {}
        stats = item.get("statistics") or {}

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

        try:
            cache.set(
                cache_key,
                result,
                ttl=self.DETAIL_CACHE_TTL,
            )
        except Exception:
            logger.exception("YouTube video cache write failed")

        return result

    @classmethod
    def is_entertainment_title(cls, title: str) -> bool:
        normalized = str(title or "").casefold()
        return any(
            term in normalized
            for term in cls.ENTERTAINMENT_TITLE_TERMS
        )

    @classmethod
    def is_entertainment(cls, text: str) -> bool:
        """Compatibility helper for older callers."""
        return cls.is_entertainment_title(text)

    @staticmethod
    def _thumbnail(snippet: dict[str, Any]) -> str:
        thumbnails = snippet.get("thumbnails") or {}

        for size in ("maxres", "high", "medium", "default"):
            url = (thumbnails.get(size) or {}).get("url")
            if url:
                return str(url)

        return ""

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0


youtube_service = YouTubeService()





