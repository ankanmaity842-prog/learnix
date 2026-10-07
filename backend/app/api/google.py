from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.services.google_auth_service import (
    google_auth_service,
)


router = APIRouter(
    prefix="/auth/google",
    tags=["Google Authentication"],
)


@router.get("/login")
async def google_login():
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth is not configured",
        )

    return RedirectResponse(
        url=google_auth_service.get_authorization_url()
    )


@router.get("/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db),
):
    try:
        token = await google_auth_service.authenticate(
            code,
            db,
        )

        redirect_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}"
            f"/oauth/callback"
            f"?token={token}"
        )

        return RedirectResponse(
            url=redirect_url
        )

    except Exception as exc:
        print(
            "Google authentication error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=400,
            detail="Google authentication failed",
        )