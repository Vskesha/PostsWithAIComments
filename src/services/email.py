from pathlib import Path
from typing import List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings
from src.database.models import User
from src.services.auth import auth_service


class EmailService:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_FROM_NAME=settings.mail_from_name,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=Path(__file__).parent / "templates",
    )

    async def send_email(
        self,
        recipients: List[EmailStr],
        subject: str,
        body: dict,
        template_filename: str,
    ):
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=body,
                subtype=MessageType.html,
            )

            fm = FastMail(self.conf)
            await fm.send_message(message, template_name=template_filename)
        except ConnectionErrors as err:
            print(err)

    async def send_verification_email(self, user: User, host: str):
        verification_token = await auth_service.create_email_token({"sub": user.email})
        body = {"host": host, "username": user.username, "token": verification_token}
        await self.send_email(
            recipients=[user.email],
            subject="Confirm your email.",
            body=body,
            template_filename="verify_email.html",
        )


email_service = EmailService()
