from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token
from app.models.user import User


GOOGLE_AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)

GOOGLE_TOKEN_URL = (
    "https://oauth2.googleapis.com/token"
)

GOOGLE_USERINFO_URL = (
    "https://www.googleapis.com/oauth2/v2/userinfo"
)


class GoogleAuthService:

    def get_authorization_url(self) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
        }

        return (
            f"{GOOGLE_AUTH_URL}?"
            f"{urlencode(params)}"
        )

    async def authenticate(
        self,
        code: str,
        db: Session,
    ) -> str:

        async with httpx.AsyncClient(
            timeout=20
        ) as client:

            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )

            if token_response.status_code != 200:
                print(
                    "Google token error:",
                    token_response.text,
                )

                raise ValueError(
                    "Google token exchange failed"
                )

            token_data = token_response.json()

            google_access_token = token_data.get(
                "access_token"
            )

            if not google_access_token:
                raise ValueError(
                    "Google access token missing"
                )

            user_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={
                    "Authorization":
                    f"Bearer {google_access_token}"
                },
            )

            if user_response.status_code != 200:
                print(
                    "Google userinfo error:",
                    user_response.text,
                )

                raise ValueError(
                    "Unable to retrieve Google profile"
                )

            google_user = user_response.json()

        google_id = google_user.get("id")
        email = google_user.get("email")

        if not google_id or not email:
            raise ValueError(
                "Google account information unavailable"
            )

        email = email.lower().strip()

        user = (
            db.query(User)
            .filter(User.google_id == google_id)
            .first()
        )

        if not user:
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

        if user:
            user.google_id = google_id
            user.auth_provider = "google"

        else:
            username = self.generate_username(
                google_user.get(
                    "name",
                    "learnixuser",
                ),
                email,
                db,
            )

            user = User(
                username=username,
                name=google_user.get(
                    "name",
                    "Learnix User",
                ),
                email=email,
                google_id=google_id,
                auth_provider="google",
                password_hash=None,
                preferred_language="en",
                is_active=True,
            )

            db.add(user)

        db.commit()
        db.refresh(user)

        return create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "username": user.username,
            }
        )

    @staticmethod
    def generate_username(
        name: str,
        email: str,
        db: Session,
    ) -> str:

        base = "".join(
            char.lower()
            for char in name
            if char.isalnum()
        )

        if len(base) < 5:
            base = (
                email.split("@")[0]
                .replace(".", "")
                .replace("_", "")
            )

        if len(base) < 5:
            base = "learnixuser"

        base = base[:25]

        username = base
        counter = 1

        while (
            db.query(User)
            .filter(User.username == username)
            .first()
        ):
            suffix = str(counter)

            username = (
                f"{base[:30-len(suffix)]}"
                f"{suffix}"
            )

            counter += 1

        return username


google_auth_service = GoogleAuthService()