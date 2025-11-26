"""Utilities for summarising company changes for notifications."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

ChangeSummary = List[Dict[str, Any]]


def _safe_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, str)):
        return value
    return str(value)


def _latest_financial_value(company: Optional[Dict[str, Any]], field: str) -> Optional[float]:
    if not company:
        return None
    if company.get(field) is not None:
        return company.get(field)
    financials = company.get("financials") or []
    for entry in financials:
        if field in entry and entry[field] is not None:
            return entry[field]
    return None


def _collect_names(items: Optional[List[Dict[str, Any]]], key: str = "full_name") -> List[str]:
    if not items:
        return []
    names: List[str] = []
    for item in items:
        value = item.get(key) or (
            f"{item.get('first_name') or ''} {item.get('last_name') or ''}".strip()
        )
        if value:
            names.append(value)
    return sorted(set(names))


def _collect_addresses(addresses: Optional[List[Dict[str, Any]]]) -> List[str]:
    if not addresses:
        return []
    formatted: List[str] = []
    for addr in addresses:
        line = " ".join(
            part
            for part in [addr.get("street"), addr.get("house_number"), addr.get("city")]
            if part
        ).strip()
        if line:
            formatted.append(line)
    return sorted(set(formatted))


def _collect_filings(filings: Optional[List[Dict[str, Any]]]) -> List[str]:
    if not filings:
        return []
    lines = []
    for filing in filings:
        label = filing.get("filing_type") or filing.get("description") or "Filing"
        date = filing.get("date") or filing.get("created_at")
        lines.append(f"{label} @ {date}")
    return sorted(set(lines))


def compute_company_changes(
    previous: Optional[Dict[str, Any]],
    current: Dict[str, Any],
) -> Tuple[ChangeSummary, Optional[str]]:
    """Compare two company payloads and return a change summary plus digest."""

    if not previous:
        return [], None

    changes: ChangeSummary = []

    def track(label: str, before: Any, after: Any) -> None:
        before_safe = _safe_value(before)
        after_safe = _safe_value(after)
        if before_safe == after_safe:
            return
        changes.append({
            "field": label,
            "before": before_safe,
            "after": after_safe,
        })

    track("Revenue", _latest_financial_value(previous, "revenue"), _latest_financial_value(current, "revenue"))
    track("Profit", _latest_financial_value(previous, "profit"), _latest_financial_value(current, "profit"))

    prev_officers = _collect_names(previous.get("officers"))
    curr_officers = _collect_names(current.get("officers"))
    if prev_officers != curr_officers:
        changes.append({
            "field": "Officers",
            "before": prev_officers,
            "after": curr_officers,
        })

    prev_addresses = _collect_addresses(previous.get("addresses"))
    curr_addresses = _collect_addresses(current.get("addresses"))
    if prev_addresses != curr_addresses:
        changes.append({
            "field": "Addresses",
            "before": prev_addresses,
            "after": curr_addresses,
        })

    prev_filings = _collect_filings(previous.get("filings"))
    curr_filings = _collect_filings(current.get("filings"))
    if prev_filings != curr_filings:
        changes.append({
            "field": "Filings",
            "before": prev_filings,
            "after": curr_filings,
        })

    prev_risks = previous.get("risks") or []
    curr_risks = current.get("risks") or []
    if len(prev_risks) != len(curr_risks):
        changes.append({
            "field": "Risks",
            "before": len(prev_risks),
            "after": len(curr_risks),
        })

    if not changes:
        return [], None

    digest_source = json.dumps(changes, sort_keys=True, default=str)
    digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()
    return changes, digest
