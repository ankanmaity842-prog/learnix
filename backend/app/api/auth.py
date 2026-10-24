
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.services.email_service import email_service


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=5, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")
    challenge_token: str
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _code_digest(
    email: str,
    code: str,
    password_hash: str,
) -> str:
    value = f"{email}:{code}:{password_hash}".encode("utf-8")
    return hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        value,
        hashlib.sha256,
    ).hexdigest()


def _password_fingerprint(password_hash: str) -> str:
    return hashlib.sha256(
        password_hash.encode("utf-8")
    ).hexdigest()


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    username = data.username.strip().lower()
    email = str(data.email).lower().strip()

    if len(username) < 5:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 5 characters",
        )

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        name=data.name.strip(),
        username=username,
        email=email,
        password_hash=hash_password(data.password),
        auth_provider="local",
        preferred_language="en",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
    })

    return {
        "message": "Registration successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
        },
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    identifier = data.identifier.strip().lower()

    user = (
        db.query(User)
        .filter(
            (User.email == identifier)
            | (User.username == identifier)
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google login",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "email": current_user.email,
        "preferred_language": current_user.preferred_language,
        "auth_provider": current_user.auth_provider,
    }


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).lower().strip()

    user = db.query(User).filter(User.email == email).first()

    generic_response = {
        "message": (
            "If an account exists for this email, "
            "a reset code has been sent."
        )
    }

    if not user or not user.password_hash:
        return generic_response

    code = f"{secrets.randbelow(1_000_000):06d}"
    now = datetime.now(timezone.utc)

    challenge_token = jwt.encode(
        {
            "type": "password_reset_code",
            "sub": str(user.id),
            "email": email,
            "code_digest": _code_digest(
                email,
                code,
                user.password_hash,
            ),
            "password_fingerprint": _password_fingerprint(
                user.password_hash,
            ),
            "exp": now + timedelta(
                minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            ),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    try:
        sent = await email_service.send_password_reset_code(
            email,
            code,
        )
    except Exception:
        logger.exception(
            "Password-reset code delivery raised an exception."
        )
        sent = False

    if not sent:
        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to send the reset code right now. "
                "Please try again later."
            ),
        )

    # Return the signed challenge only to the requesting client.
    # The OTP itself is never returned by this endpoint.
    return {
        **generic_response,
        "challenge_token": challenge_token,
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).lower().strip()

    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )

    try:
        payload = jwt.decode(
            data.challenge_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail=(
                "The reset code has expired or the reset session "
                "is invalid. Request a new code."
            ),
        )

    if payload.get("type") != "password_reset_code":
        raise HTTPException(
            status_code=400,
            detail="Invalid reset session",
        )

    if str(payload.get("email", "")).lower().strip() != email:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset session",
        )

    user_id = payload.get("sub")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid reset session",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.email.lower().strip() != email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or reset session",
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=400,
            detail="This account cannot use password reset",
        )

    current_fingerprint = _password_fingerprint(user.password_hash)

    if not hmac.compare_digest(
        str(payload.get("password_fingerprint", "")),
        current_fingerprint,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "This reset code has already been used. "
                "Request a new code."
            ),
        )

    expected_digest = _code_digest(
        email,
        data.code,
        user.password_hash,
    )
    token_digest = str(payload.get("code_digest", ""))

    if not hmac.compare_digest(token_digest, expected_digest):
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code",
        )

    user.password_hash = hash_password(data.password)
    user.auth_provider = "local"

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Unable to save the new password.")
        raise HTTPException(
            status_code=500,
            detail="Unable to update the password. Please try again.",
        )

    return {
        "message": "Password changed successfully. You can now log in."
    }

