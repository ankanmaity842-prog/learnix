from app.utils.text_processing import (
    clean_text,
    sentence_count,
    tokenize_text,
    word_count,
)


def test_clean_text():
    text = "  Machine   Learning   is   useful.  "

    result = clean_text(text)

    assert result == "Machine Learning is useful."


def test_tokenize_text():
    text = "Machine Learning"

    tokens = tokenize_text(text)

    assert tokens == [
        "machine",
        "learning",
    ]


def test_word_count():
    assert word_count(
        "Machine learning is useful"
    ) == 5


def test_sentence_count():
    text = "Machine learning is useful. AI is powerful."

    assert sentence_count(text) == 2