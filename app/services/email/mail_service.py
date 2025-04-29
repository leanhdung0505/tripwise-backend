from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging

import emails
from jinja2 import Template
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class EmailData:
    subject: str
    html_content: str

def render_email_template(template_name: str, context: dict[str, Any]) -> str:
    template_path = Path(__file__).parent.parent.parent / "email-templates" / "build" / template_name
    try:
        template_str = template_path.read_text(encoding="utf-8")
        return Template(template_str).render(context)
    except FileNotFoundError:
        logger.error(f"Email template not found: {template_name}")
        raise HTTPException(status_code=500, detail="Email template not found")

def send_email(email_to: str, subject: str, html_content: str) -> None:
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        charset="utf-8"
    )

    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "tls": settings.SMTP_TLS,
        "ssl": settings.SMTP_SSL,
        "user": settings.SMTP_USER,
        "password": settings.SMTP_PASSWORD,
    }
    logger.error(f"{smtp_options}")
    try:
        response = message.send(to=email_to, smtp={k: v for k, v in smtp_options.items() if v})
        if not response.status_code == 250:
            logger.error(f"Failed to send email to {email_to}: {response.error}")
            raise HTTPException(status_code=500, detail="Failed to send email")
        logger.info(f"Email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Error sending email to {email_to}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")

def create_verification_email(email_to: str, otp_code: str) -> EmailData:
    subject = f"{settings.PROJECT_NAME} - Email Verification Code"
    html = render_email_template("new_account.html", {
        "project_name": settings.PROJECT_NAME,
        "email": email_to,
        "otp_code": otp_code,
        "logo_url": f"{settings.FRONTEND_HOST}/assets/images/logo.png"
    })
    return EmailData(subject=subject, html_content=html)

def create_recovery_email(email_to: str, otp_code: str, full_name: str) -> EmailData:
    subject = f"{settings.PROJECT_NAME} - Password Recovery Code"
    html = render_email_template("reset_password.html", {
        "project_name": settings.PROJECT_NAME,
        "email": email_to,
        "otp_code": otp_code,
        "valid_minutes": 5,
        "full_name": full_name  # Thêm full_name vào context
    })
    return EmailData(subject=subject, html_content=html)