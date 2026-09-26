import pytest

from app.utils.validators import (
    validate_language,
    validate_positive_integer,
    validate_score,
)


def test_supported_languages():
    assert validate_language("en") == "en"
    assert validate_language("bn") == "bn"
    assert validate_language("hi") == "hi"


def test_language_is_normalized():
    assert validate_language("EN") == "en"


def test_invalid_language():
    with pytest.raises(ValueError):
        validate_language("fr")


def test_positive_integer():
    assert validate_positive_integer(10) == 10


def test_invalid_integer():
    with pytest.raises(ValueError):
        validate_positive_integer(0)


def test_valid_score():
    assert validate_score(0.75) == 0.75


def test_invalid_score():
    with pytest.raises(ValueError):
        validate_score(1.5)