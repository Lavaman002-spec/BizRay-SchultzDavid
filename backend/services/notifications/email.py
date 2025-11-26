"""Minimal email delivery helper using the Resend API."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from backend.shared.config import RESEND_API_KEY, NOTIFICATIONS_FROM_EMAIL

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


def send_email(
    *,
    to: str,
    subject: str,
    html: str,
    text: Optional[str] = None,
) -> bool:
    """Send an email if credentials are configured."""

    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured; skipping email delivery")
        return False

    payload = {
        "from": NOTIFICATIONS_FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(
                RESEND_ENDPOINT,
                json=payload,
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to send email via Resend: %s", exc)
        return False

    return True
