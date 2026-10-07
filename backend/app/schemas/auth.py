from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=128,
    )


class LoginRequest(BaseModel):
    identifier: str = Field(
        min_length=1,
        max_length=255,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str

    password: str = Field(
        min_length=6,
        max_length=128,
    )

    confirm_password: str = Field(
        min_length=6,
        max_length=128,
    )


class ChangePasswordRequest(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=6,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    auth_provider: str


class MessageResponse(BaseModel):
    message: str