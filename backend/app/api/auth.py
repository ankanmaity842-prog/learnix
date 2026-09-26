import secrets
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=5, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        password_hash,
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": email,
        "purpose": "password_reset",
        "exp": expire,
        "nonce": secrets.token_hex(8),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    username = data.username.strip().lower()
    email = data.email.lower()

    if len(username) < 5:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 5 characters",
        )

    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        name=data.name.strip(),
        username=username,
        email=email,
        password_hash=hash_password(data.password),
        preferred_language="en",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

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

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    return {
        "access_token": create_access_token(user.id),
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
    }


@router.post("/logout")
async def logout():
    return {
        "message": "Logged out successfully"
    }


@router.get("/google")
async def google_login():
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth is not configured",
        )

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }

    query = "&".join(
        f"{key}={httpx.QueryParams({key: value})[key]}"
        for key, value in params.items()
    )

    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{query}"
    )


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db),
):
    token_url = "https://oauth2.googleapis.com/token"

    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            token_url,
            data=token_data,
        )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Google authorization failed",
        )

    tokens = token_response.json()

    async with httpx.AsyncClient(timeout=15) as client:
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={
                "Authorization": (
                    f"Bearer {tokens['access_token']}"
                )
            },
        )

    if user_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Unable to retrieve Google profile",
        )

    google_user = user_response.json()

    email = google_user.get("email")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account email unavailable",
        )

    email = email.lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        base_username = (
            google_user.get("name", "learner")
            .lower()
            .replace(" ", "")
        )

        base_username = "".join(
            character
            for character in base_username
            if character.isalnum()
        )

        base_username = (
            base_username[:24]
            if len(base_username) >= 5
            else "learner"
        )

        username = base_username
        counter = 1

        while (
            db.query(User)
            .filter(User.username == username)
            .first()
        ):
            suffix = str(counter)
            username = (
                f"{base_username[:30-len(suffix)]}{suffix}"
            )
            counter += 1

        user = User(
            name=google_user.get(
                "name",
                "Learnix User",
            ),
            username=username,
            email=email,
            password_hash=hash_password(
                secrets.token_urlsafe(32)
            ),
            preferred_language="en",
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)

    frontend_url = (
        f"{settings.FRONTEND_URL}"
        f"/oauth/callback?token={token}"
    )

    return RedirectResponse(frontend_url)


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == data.email.lower())
        .first()
    )

    if user:
        reset_token = create_reset_token(user.email)

        reset_url = (
            f"{settings.FRONTEND_URL}"
            f"/reset-password?token={reset_token}"
        )

        print(
            f"Password reset link for {user.email}: "
            f"{reset_url}"
        )

    return {
        "message": (
            "If an account exists for this email, "
            "a password reset link has been sent."
        )
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )

    try:
        payload = jwt.decode(
            data.token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("purpose") != "password_reset":
            raise HTTPException(
                status_code=400,
                detail="Invalid password reset token",
            )

        email = payload.get("sub")

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset token",
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.password_hash = hash_password(
        data.password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }