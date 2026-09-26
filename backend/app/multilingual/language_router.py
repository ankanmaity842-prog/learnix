from typing import Any

from app.multilingual.language_detector import (
    detect_language,
)


SUPPORTED_LANGUAGES = {
    "en": "English",
    "bn": "Bengali",
    "hi": "Hindi",
}


class LanguageRouter:

    def detect(
        self,
        text: str,
    ) -> dict[str, Any]:

        return detect_language(text)

    def validate(
        self,
        language: str,
    ) -> str:

        if language in SUPPORTED_LANGUAGES:
            return language

        return "en"

    def route(
        self,
        text: str,
        preferred_language: str | None = None,
    ) -> dict[str, Any]:

        if preferred_language:
            language = self.validate(
                preferred_language
            )

            return {
                "language": language,
                "language_name": SUPPORTED_LANGUAGES[
                    language
                ],
                "source": "preference",
            }

        detected = self.detect(text)

        return {
            **detected,
            "source": "detection",
        }


language_router = LanguageRouter()