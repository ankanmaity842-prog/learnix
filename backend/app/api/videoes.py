from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/videos", tags=["Videos"])


class VideoResponse(BaseModel):
    video_id: str
    title: str
    description: Optional[str] = None
    channel: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    published_at: Optional[str] = None


@router.get("/{video_id}")
async def get_video(video_id: str):
    """
    Get details of a specific educational video.
    """

    if not video_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Video ID is required",
        )

    return {
        "video_id": video_id,
        "title": "Educational Video",
        "description": "",
        "channel": "",
        "thumbnail": "",
        "duration": "",
        "published_at": "",
    }


@router.get("/{video_id}/transcript")
async def get_transcript(video_id: str, language: str = "en"):
    """
    Retrieve transcript for a video.
    """

    return {
        "video_id": video_id,
        "language": language,
        "transcript": "",
        "segments": [],
    }


@router.get("/{video_id}/analysis")
async def get_video_analysis(video_id: str):
    """
    Return combined NLP + computer vision analysis.
    """

    return {
        "video_id": video_id,
        "transcript_analysis": {
            "difficulty": None,
            "readability": None,
            "topic_relevance": None,
        },
        "visual_analysis": {
            "slide_count": 0,
            "diagram_count": 0,
            "code_frames": 0,
            "visual_complexity": None,
        },
    }