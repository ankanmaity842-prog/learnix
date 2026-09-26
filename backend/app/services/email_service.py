import smtplib
from email.message import EmailMessage

from app.config import settings


class EmailService:

    def send_password_reset_email(
        self,
        email: str,
        reset_url: str,
    ) -> None:

        if not settings.SMTP_HOST:
            raise RuntimeError(
                "SMTP is not configured"
            )

        message = EmailMessage()

        message["Subject"] = (
            "Reset your Learnix password"
        )
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = email

        message.set_content(
            f"""
Hello,

We received a request to reset your Learnix password.

Use the following link to create a new password:

{reset_url}

This link will expire soon.

If you did not request this password reset,
you can safely ignore this email.

Learnix
"""
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        ) as server:

            if settings.SMTP_USE_TLS:
                server.starttls()

            if (
                settings.SMTP_USERNAME
                and settings.SMTP_PASSWORD
            ):
                server.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD,
                )

            server.send_message(message)


email_service = EmailService()