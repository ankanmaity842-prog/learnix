from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_is_different_from_plain_password():
    password = "StrongPassword123"

    hashed = hash_password(password)

    assert hashed != password


def test_password_verification():
    password = "StrongPassword123"

    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_access_token_creation_and_decoding():
    token = create_access_token(
        {
            "sub": "1",
        }
    )

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"