SUPPORTED_LANGUAGES = {
    "en",
    "bn",
    "hi",
}


def validate_language(
    language: str,
) -> str:
    language = language.lower().strip()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: en, bn, hi."
        )

    return language


def validate_positive_integer(
    value: int,
    field_name: str = "value",
) -> int:
    if value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return value


def validate_score(
    score: float,
) -> float:
    if not 0.0 <= score <= 1.0:
        raise ValueError(
            "Score must be between 0 and 1."
        )

    return score