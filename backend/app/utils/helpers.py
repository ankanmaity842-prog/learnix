from collections.abc import Iterable


def chunk_text(
    text: str,
    max_words: int = 500,
) -> list[str]:
    if not text:
        return []

    words = text.split()

    if max_words <= 0:
        raise ValueError(
            "max_words must be greater than zero."
        )

    return [
        " ".join(words[index:index + max_words])
        for index in range(
            0,
            len(words),
            max_words,
        )
    ]


def safe_float(
    value,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(
    value,
    default: int = 0,
) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def unique_preserve_order(
    items: Iterable,
) -> list:
    seen = set()
    result = []

    for item in items:
        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result