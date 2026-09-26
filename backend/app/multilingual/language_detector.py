from typing import Any

from langdetect import detect_langs


SUPPORTED_LANGUAGES = {
    "en": "English",
    "bn": "Bengali",
    "hi": "Hindi",
}


def detect_language(
    text: str,
) -> dict[str, Any]:

    if not text.strip():
        return {
            "language": "en",
            "language_name": "English",
            "confidence": 0.0,
        }

    try:
        detected = detect_langs(text)[0]

        language = detected.lang
        confidence = float(
            detected.prob
        )

        if language not in SUPPORTED_LANGUAGES:
            language = "en"
            confidence = 0.0

        return {
            "language": language,
            "language_name": SUPPORTED_LANGUAGES[
                language
            ],
            "confidence": round(
                confidence,
                4,
            ),
        }

    except Exception:
        return {
            "language": "en",
            "language_name": "English",
            "confidence": 0.0,
        }