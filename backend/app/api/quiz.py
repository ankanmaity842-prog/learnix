
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.transcript_service import transcript_service
from app.services.quiz_service import quiz_service

router = APIRouter(prefix="/quiz", tags=["Quiz"])


class QuizRequest(BaseModel):
    video_id: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    content: str = ""
    language: Literal["en", "hi", "bn"] = "en"
    number_of_questions: int = Field(default=10, ge=1, le=20)
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class TranscriptRequest(BaseModel):
    language: Literal["en", "hi", "bn"] = "en"


@router.get("/transcript/{video_id}")
async def get_video_transcript(
    video_id: str,
    language: Literal["en", "hi", "bn"] = "en",
):
    result = await transcript_service.get_transcript(
        video_id=video_id,
        language=language,
    )

    if not result["available"]:
        raise HTTPException(
            status_code=404,
            detail=(
                "Captions are unavailable for this video. "
                "Please provide lesson notes to generate a quiz."
            ),
        )

    return result


@router.post("/generate")
async def generate_quiz(data: QuizRequest):
    content = data.content.strip()

    if not content:
        transcript = await transcript_service.get_transcript(
            video_id=data.video_id,
            language=data.language,
        )

        if not transcript["available"]:
            raise HTTPException(
                status_code=422,
                detail=(
                    "This video has no accessible transcript. "
                    "Paste lesson notes and try again."
                ),
            )

        content = transcript["text"]

    try:
        result = await quiz_service.generate(
            topic=data.topic,
            content=content,
            language=data.language,
            number_of_questions=data.number_of_questions,
            difficulty=data.difficulty,
        )

        return {
            "video_id": data.video_id,
            **result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
