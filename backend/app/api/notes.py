from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/notes",
    tags=["AI Notes"],
)


class NotesRequest(BaseModel):
    topic: str
    content: str
    language: str = "en"
    detail_level: str = "medium"


def build_notes(data: NotesRequest):
    return {
        "topic": data.topic,
        "language": data.language,
        "detail_level": data.detail_level,
        "notes": {
            "summary": "",
            "key_points": [],
            "definitions": [],
            "examples": [],
        },
    }


@router.post("/")
async def generate_notes(
    data: NotesRequest,
    current_user: User = Depends(get_current_user),
):
    return build_notes(data)


@router.post("/generate")
async def generate_notes_explicit(
    data: NotesRequest,
    current_user: User = Depends(get_current_user),
):
    return build_notes(data)


@router.get("/{topic}")
async def get_notes(
    topic: str,
    language: str = "en",
    current_user: User = Depends(get_current_user),
):
    return {
        "topic": topic,
        "language": language,
        "notes": None,
    }