import re


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = re.sub(
        r"[^\S\r\n]+",
        " ",
        text,
    )

    return text.strip()


def tokenize_text(text: str) -> list[str]:
    cleaned = clean_text(text)

    if not cleaned:
        return []

    return re.findall(
        r"\b\w+\b",
        cleaned.lower(),
        flags=re.UNICODE,
    )


def word_count(text: str) -> int:
    return len(tokenize_text(text))


def sentence_count(text: str) -> int:
    cleaned = clean_text(text)

    if not cleaned:
        return 0

    sentences = re.split(
        r"[.!?]+",
        cleaned,
    )

    return len(
        [
            sentence
            for sentence in sentences
            if sentence.strip()
        ]
    )