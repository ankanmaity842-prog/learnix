from typing import Any


class TranscriptService:

    async def get_transcript(
        self,
        video_id: str,
        language: str = "en",
    ) -> dict[str, Any]:

        try:
            from youtube_transcript_api import (
                YouTubeTranscriptApi,
            )

            api = YouTubeTranscriptApi()

            transcript = api.fetch(
                video_id,
                languages=[language],
            )

            segments = []

            for item in transcript:
                text = getattr(
                    item,
                    "text",
                    "",
                )

                start = getattr(
                    item,
                    "start",
                    0.0,
                )

                duration = getattr(
                    item,
                    "duration",
                    0.0,
                )

                if not text:
                    continue

                segments.append(
                    {
                        "text": text,
                        "start": float(start),
                        "duration": float(duration),
                    }
                )

            text = " ".join(
                segment["text"]
                for segment in segments
            )

            return {
                "video_id": video_id,
                "language": language,
                "text": text,
                "segments": segments,
                "available": bool(text.strip()),
            }

        except Exception:
            return {
                "video_id": video_id,
                "language": language,
                "text": "",
                "segments": [],
                "available": False,
            }


transcript_service = TranscriptService()