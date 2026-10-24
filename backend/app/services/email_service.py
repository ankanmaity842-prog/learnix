
import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    async def send_password_reset_code(
        self,
        email: str,
        code: str,
    ) -> bool:
        environment = settings.ENVIRONMENT.strip().lower()

        if environment in {"development", "local"}:
            logger.warning(
                "[LOCAL DEVELOPMENT ONLY] Password reset OTP "
                "for %s: %s",
                email,
                code,
            )
            return True

        required_values = (
            settings.SMTP_HOST,
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD,
            settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME,
        )

        if not all(required_values):
            logger.error(
                "Password-reset email failed: SMTP settings "
                "are incomplete."
            )
            return False

        message = EmailMessage()
        message["Subject"] = "Your Learnix password reset code"
        message["From"] = (
            settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
        )
        message["To"] = email
        message.set_content(
            f"""Hello,

Your Learnix password reset code is: {code}

This code expires in
{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.

If you did not request a password reset, you can ignore
this email.

Learnix Team
"""
        )

        try:
            await asyncio.to_thread(
                self._send_smtp,
                message,
            )
            return True
        except Exception:
            # Do not log the OTP, message body, or SMTP password.
            logger.exception(
                "Unable to deliver the password-reset email."
            )
            return False

    @staticmethod
    def _send_smtp(message: EmailMessage) -> None:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=20,
        ) as server:
            server.ehlo()

            if settings.SMTP_USE_TLS:
                server.starttls()
                server.ehlo()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )
            server.send_message(message)


email_service = EmailService()

