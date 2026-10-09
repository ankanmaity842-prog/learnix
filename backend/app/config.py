
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = True
    APP_NAME: str = "Learnix"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    YOUTUBE_API_KEY: str
    GEMINI_API_KEY: str

    # Optional for tests and environments without Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = (
        "http://localhost:8000/auth/google/callback"
    )

    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
