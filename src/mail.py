from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from src.config import settings

import os

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.email.username,
    MAIL_PASSWORD=settings.email.password,
    MAIL_FROM=settings.email.mail_from,
    MAIL_PORT=settings.email.port,
    MAIL_SERVER=settings.email.server,
    MAIL_STARTTLS=settings.email.starttls,
    MAIL_SSL_TLS=settings.email.ssl_tls,
    USE_CREDENTIALS=settings.email.use_credentials,
    SUPPRESS_SEND=1 if os.getenv("TESTING") else 0
)

fm = FastMail(mail_conf)

async def send_task_notification(subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[settings.email.mail_from],
        body=body,
        subtype=MessageType.html
    )
    await fm.send_message(message)
