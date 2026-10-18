"""Outbound email over stdlib smtplib.

Configured entirely by environment (see config.py SMTP_*). Every send is
fail-soft: False is returned when unconfigured or on error, and callers
must never leak delivery state (anti-enumeration).
"""
import logging
import smtplib
from email.message import EmailMessage

import config

logger = logging.getLogger(__name__)


def smtp_configured() -> bool:
    return bool(config.SMTP_HOST)


def send_password_reset_email(to_email: str, token: str) -> bool:
    """Email a 15-minute reset link. Returns True only if accepted by SMTP."""
    if not smtp_configured():
        return False
    reset_url = f"{config.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Reset your RecruitAI password"
    msg["From"] = config.SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        "Someone requested a password reset for your RecruitAI account.\n\n"
        f"Open this link within 15 minutes to choose a new password:\n{reset_url}\n\n"
        "If you did not request this, you can safely ignore this email."
    )
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as smtp:
            if config.SMTP_USE_TLS:
                smtp.starttls()
            if config.SMTP_USER:
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        logger.warning("SMTP password-reset send failed: %s", exc)
        return False
