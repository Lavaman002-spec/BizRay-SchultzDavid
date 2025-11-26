"""Notification dispatchers for watchlisted companies."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from backend.database.client import get_supabase_client
from backend.services.notifications.email import send_email
from backend.shared.config import APP_BASE_URL

logger = logging.getLogger(__name__)


def _resolve_user_email(
    client,
    user_id: Optional[str],
    fallback: Optional[str],
    cache: Dict[str, Optional[str]],
) -> Optional[str]:
    """Fetch the latest email for a user via Supabase Admin, cached per request."""
    if not user_id:
        return fallback

    if user_id in cache:
        return cache[user_id]

    email = fallback
    try:
        response = client.auth.admin.get_user_by_id(user_id)
        if response and getattr(response, "user", None):
            email = response.user.email or fallback
    except Exception as exc:  # pragma: no cover - best effort fetch
        logger.debug("Unable to resolve email for user %s: %s", user_id, exc)

    cache[user_id] = email
    return email


def _render_change_lines(changes: List[Dict[str, object]]) -> str:
    lines = []
    for change in changes:
        before = change.get("before")
        after = change.get("after")
        if isinstance(before, list):
            before = ", ".join(str(item) for item in before)
        if isinstance(after, list):
            after = ", ".join(str(item) for item in after)
        lines.append(f"<li><strong>{change['field']}:</strong> {before} → {after}</li>")
    return "".join(lines)


def dispatch_watchlist_notifications(
    company: Dict[str, object],
    changes: List[Dict[str, object]],
    digest: str,
) -> None:
    if not changes or not digest:
        return

    company_id = company.get("id")
    if company_id is None:
        return

    client = get_supabase_client()
    response = (
        client.table("user_watchlist")
        .select("id, user_id, user_email, notify_via_email, last_change_digest")
        .eq("company_id", company_id)
        .execute()
    )
    watchers = response.data or []
    if not watchers:
        return

    lines_html = _render_change_lines(changes)
    subject = f"BizRay: {company.get('name')} updated"
    company_link = f"{APP_BASE_URL}/company/{company_id}"
    html = (
        f"<p>Updates were detected for <strong>{company.get('name')}</strong>.</p>"
        f"<ul>{lines_html}</ul>"
        f"<p><a href='{company_link}'>View the company in BizRay</a></p>"
    )
    text_lines = [
        f"Updates for {company.get('name')}",
        *(f"- {change['field']}: {change.get('before')} -> {change.get('after')}" for change in changes),
        f"View: {company_link}",
    ]
    text_body = "\n".join(text_lines)

    notified_ids: List[int] = []

    email_cache: Dict[str, Optional[str]] = {}

    for watcher in watchers:
        if not watcher.get("notify_via_email", True):
            continue
        if watcher.get("last_change_digest") == digest:
            continue
        email = _resolve_user_email(
            client,
            watcher.get("user_id"),
            watcher.get("user_email"),
            email_cache,
        )
        if not email:
            continue
        if send_email(to=email, subject=subject, html=html, text=text_body):
            notified_ids.append(watcher["id"])
            try:
                client.table("alerts").insert(
                    {
                        "user_id": watcher["user_id"],
                        "company_id": company_id,
                        "type": "company_change",
                        "message": text_body,
                    }
                ).execute()
            except Exception as exc:  # pragma: no cover - logging only
                logger.debug("Failed to record alert for watcher %s: %s", watcher["id"], exc)

    if not notified_ids:
        return

    timestamp = datetime.utcnow().isoformat()
    for watchlist_id in notified_ids:
        try:
            client.table("user_watchlist").update(
                {"last_notified_at": timestamp, "last_change_digest": digest}
            ).eq("id", watchlist_id).execute()
        except Exception as exc:  # pragma: no cover
            logger.debug(
                "Failed to update notification metadata for watchlist %s: %s",
                watchlist_id,
                exc,
            )
