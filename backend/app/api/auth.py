from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
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


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    username: str = Field(
        ...,
        min_length=5,
        max_length=30,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )


class LoginRequest(BaseModel):
    identifier: str = Field(
        ...,
        min_length=1,
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )

    confirm_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
        auth_provider="local",
        preferred_language="en",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }
    )

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


@router.post(
    "/login",
    response_model=TokenResponse,
)
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

    if not verify_password(
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

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }
    )

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
    return {
        "message": "Logged out successfully",
    }


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == str(data.email).lower())
        .first()
    )

    if user:
        from app.core.security import create_password_reset_token

        reset_token = create_password_reset_token(user.id)

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

        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=400,
                detail="Invalid password reset token",
            )

        user_id = payload.get("sub")

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset token",
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
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

    user.auth_provider = "local"

    db.commit()

    return {
        "message": "Password changed successfully",
    }