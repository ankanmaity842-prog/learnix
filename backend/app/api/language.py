from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/languages", tags=["Languages"])


SUPPORTED_LANGUAGES = {
    "en": "English",
    "bn": "Bengali",
    "hi": "Hindi",
}


class LanguageRequest(BaseModel):
    text: str


@router.get("/")
async def supported_languages():
    """
    Return supported application languages.
    """

    return {
        "languages": SUPPORTED_LANGUAGES
    }


@router.post("/detect")
async def detect_language(data: LanguageRequest):
    """
    Detect the language of user input.
    """

    # Real implementation should use the multilingual
    # language detection service.

    return {
        "text": data.text,
        "language": "en",
        "language_name": "English",
        "confidence": 0.0,
    }


@router.get("/{language_code}")
async def get_language(language_code: str):
    """
    Return language information.
    """

    if language_code not in SUPPORTED_LANGUAGES:
        return {
            "supported": False,
            "language_code": language_code,
        }

    return {
        "supported": True,
        "language_code": language_code,
        "language_name": SUPPORTED_LANGUAGES[language_code],
    }