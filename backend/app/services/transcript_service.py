
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi


class TranscriptService:

    async def get_transcript(
        self,
        video_id: str,
        language: str = "en",
    ) -> dict[str, Any]:
        try:
            api = YouTubeTranscriptApi()

            transcript = api.fetch(
                video_id,
                languages=[language],
            )

            segments = []

            for item in transcript:
                text = getattr(item, "text", "").strip()

                if not text:
                    continue

                segments.append({
                    "text": text,
                    "start": float(getattr(item, "start", 0)),
                    "duration": float(getattr(item, "duration", 0)),
                })

            full_text = " ".join(
                segment["text"] for segment in segments
            )

            return {
                "video_id": video_id,
                "language": language,
                "text": full_text,
                "segments": segments,
                "available": bool(full_text.strip()),
                "error": None,
            }

        except Exception as exc:
            return {
                "video_id": video_id,
                "language": language,
                "text": "",
                "segments": [],
                "available": False,
                "error": str(exc),
            }


transcript_service = TranscriptService()
