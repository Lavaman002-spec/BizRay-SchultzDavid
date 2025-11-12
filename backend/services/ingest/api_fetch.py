"""High-level helpers for fetching and persisting Firmenbuch company data."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from database import queries as db_queries
from services.ingest.api_client import FirmenbuchAPIClient, FirmenbuchAPIError
from shared.utils import normalize_fn_number

logger = logging.getLogger(__name__)


class FirmenbuchCompanyNotFound(Exception):
    """Raised when the Firmenbuch API does not have a record for the requested company."""


class FirmenbuchFetchError(Exception):
    """Raised when fetching or persisting Firmenbuch data fails."""


def fetch_company_profile_if_missing(
    fnr: str,
    *,
    client: Optional[FirmenbuchAPIClient] = None,
) -> Dict[str, Any]:
    """Return a company record, fetching it from Firmenbuch if not yet cached."""

    normalized_fnr = normalize_fn_number(fnr)
    existing = db_queries.get_company_with_details_by_fnr(normalized_fnr)
    if existing:
        logger.debug("Company %s returned from local cache", normalized_fnr)
        return existing

    client = client or FirmenbuchAPIClient()
    logger.info("Fetching company %s from Firmenbuch API", normalized_fnr)

    try:
        payload = client.get_company_profile(normalized_fnr)
    except FirmenbuchAPIError as exc:
        logger.exception("Firmenbuch API error while fetching %s", normalized_fnr)
        raise FirmenbuchFetchError(str(exc)) from exc

    if not payload:
        logger.warning("Firmenbuch record %s not found", normalized_fnr)
        raise FirmenbuchCompanyNotFound(f"Company with FNR {normalized_fnr} not found")

    try:
        (
            company_data,
            addresses,
            officers,
            activities,
        ) = _normalise_company_payload(payload, normalized_fnr)
    except ValueError as exc:
        logger.warning(
            "Firmenbuch payload for %s missing company name: %s",
            normalized_fnr,
            exc,
        )
        raise FirmenbuchFetchError(str(exc)) from exc

    try:
        saved_company = db_queries.create_company_with_relations(
            company_data,
            addresses=addresses,
            officers=officers,
            activities=activities,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to persist Firmenbuch company %s", normalized_fnr)
        raise FirmenbuchFetchError(f"Failed to save company data: {exc}") from exc

    logger.info("Company %s stored in local database", normalized_fnr)
    return saved_company


def fetch_company_profile_by_name_if_missing(
    name: str,
    *,
    client: Optional[FirmenbuchAPIClient] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Search Firmenbuch by name and ensure the best match is cached locally."""

    search_query = (name or "").strip()
    if not search_query:
        raise ValueError("name must be provided")

    client = client or FirmenbuchAPIClient()

    logger.info("Searching Firmenbuch for company name '%s'", search_query)

    try:
        matches = client.search_companies(search_query, limit=limit)
    except FirmenbuchAPIError as exc:
        logger.exception(
            "Firmenbuch search failed for '%s'", search_query
        )
        raise FirmenbuchFetchError(str(exc)) from exc

    if not matches:
        logger.info("No Firmenbuch matches found for '%s'", search_query)
        raise FirmenbuchCompanyNotFound(
            f"No Firmenbuch match found for query '{search_query}'"
        )

    # Prefer exact (case-insensitive) matches but fall back to the first entry.
    def _candidate_key(candidate: Dict[str, Any]) -> int:
        candidate_name = _clean_string(
            candidate.get("name")
            or candidate.get("companyName")
            or candidate.get("company_name")
            or candidate.get("firmenwortlaut")
        )
        if candidate_name and candidate_name.lower() == search_query.lower():
            return 0
        return 1

    ordered_matches = sorted(matches, key=_candidate_key)

    for candidate in ordered_matches:
        fnr = _extract_candidate_fnr(candidate)
        if not fnr:
            logger.debug("Skipping Firmenbuch candidate without FNR: %s", candidate)
            continue

        try:
            fetched_company = fetch_company_profile_if_missing(fnr, client=client)
        except FirmenbuchCompanyNotFound:
            logger.info(
                "Firmenbuch record %s not available when resolving '%s'", fnr, search_query
            )
            continue
        except FirmenbuchFetchError as exc:
            logger.warning(
                "Firmenbuch fetch failed for candidate %s (%s): %s",
                fnr,
                search_query,
                exc,
            )
            continue

        logger.info(
            "Resolved Firmenbuch search for '%s' to company %s",
            search_query,
            fetched_company.get("fnr"),
        )
        return fetched_company

    raise FirmenbuchCompanyNotFound(
        f"No Firmenbuch match with a valid register number for query '{search_query}'"
    )


def _normalise_company_payload(
    payload: Dict[str, Any], fnr: str
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Convert Firmenbuch payload into structures suitable for persistence."""

    company_payload = payload.get("company") or payload

    company_name = _extract_company_name(company_payload)
    if not company_name:
        raise ValueError("Company payload missing a valid name")

    company_data = {
        "fnr": fnr,
        "name": company_name,
        "legal_form": _extract_legal_form(company_payload),
        "state": _clean_string(
            company_payload.get("status")
            or company_payload.get("state")
            or company_payload.get("companyStatus")
        ),
        "city": None,
        "last_fetched_at": datetime.utcnow().isoformat(),
    }

    addresses = _extract_addresses(company_payload)
    if addresses:
        company_data["city"] = addresses[0].get("city")
        if not company_data.get("state"):
            company_data["state"] = addresses[0].get("state")

    officers = _extract_officers(company_payload)
    activities = _extract_activities(company_payload)

    return company_data, addresses, officers, activities


def _extract_company_name(company_payload: Dict[str, Any]) -> Optional[str]:
    if not isinstance(company_payload, dict):
        return None

    candidate_keys = ("name", "companyName", "company_name", "firmenwortlaut")
    lower_key_map = {str(key).lower(): value for key, value in company_payload.items()}

    for key in candidate_keys:
        value = lower_key_map.get(key.lower())
        if value is None:
            continue
        cleaned = _extract_string_value(value)
        if cleaned:
            return cleaned

    return None


def _extract_string_value(value: Any) -> Optional[str]:
    """Return the first usable string contained within value."""

    if isinstance(value, str) or not isinstance(value, (dict, list, tuple, set)):
        return _clean_string(value)

    if isinstance(value, dict):
        value_map = {str(key).lower(): inner for key, inner in value.items()}
        candidate_keys = (
            "text",
            "value",
            "name",
            "companyname",
            "company_name",
            "label",
            "title",
            "description",
        )
        for key in candidate_keys:
            inner_value = value_map.get(key)
            if inner_value is None:
                continue
            cleaned = _extract_string_value(inner_value)
            if cleaned:
                return cleaned

        for inner_value in value.values():
            cleaned = _extract_string_value(inner_value)
            if cleaned:
                return cleaned

        return None

    for item in value:
        cleaned = _extract_string_value(item)
        if cleaned:
            return cleaned

    return None


def _extract_legal_form(company_payload: Dict[str, Any]) -> Optional[str]:
    legal_form = company_payload.get("legalForm") or company_payload.get("legal_form")
    if isinstance(legal_form, dict):
        return _clean_string(legal_form.get("text") or legal_form.get("name"))
    return _clean_string(legal_form)


def _extract_addresses(company_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_addresses: List[Dict[str, Any]] = []

    if isinstance(company_payload.get("addresses"), list):
        raw_addresses = list(company_payload.get("addresses") or [])
    elif company_payload.get("address"):
        raw_addresses = [company_payload.get("address")]
    elif company_payload.get("registeredOffice"):
        raw_addresses = [company_payload.get("registeredOffice")]

    addresses: List[Dict[str, Any]] = []
    for entry in raw_addresses:
        if not isinstance(entry, dict):
            continue
        address = {
            "street": _clean_string(
                entry.get("street")
                or entry.get("streetName")
                or entry.get("street_name")
            ),
            "house_number": _clean_string(entry.get("houseNumber") or entry.get("house_number")),
            "stairway": _clean_string(entry.get("stairway")),
            "door_number": _clean_string(entry.get("doorNumber") or entry.get("door_number")),
            "postal_code": _clean_string(entry.get("postalCode") or entry.get("postal_code")),
            "city": _clean_string(
                entry.get("city")
                or entry.get("municipality")
                or entry.get("town")
            ),
            "state": _clean_string(entry.get("state") or entry.get("province")),
            "country": _clean_string(entry.get("country")) or "Austria",
            "is_deliverable": entry.get("isDeliverable", True),
            "is_active": entry.get("isActive", True),
            "vnr": _clean_string(entry.get("vnr") or entry.get("version")),
        }
        addresses.append(address)

    return addresses


def _extract_officers(company_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_officers = company_payload.get("officers") or company_payload.get("persons") or []
    officers: List[Dict[str, Any]] = []

    for entry in raw_officers:
        if not isinstance(entry, dict):
            continue

        first_name = _clean_string(entry.get("firstName") or entry.get("first_name"))
        last_name = _clean_string(entry.get("lastName") or entry.get("last_name"))
        full_name = _clean_string(entry.get("fullName") or entry.get("full_name"))

        if not full_name:
            full_name = " ".join(filter(None, [entry.get("title"), first_name, last_name])).strip() or None

        officer = {
            "title": _clean_string(entry.get("title")),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "role": _clean_string(entry.get("role") or entry.get("function")),
            "birth_date": _clean_string(entry.get("birthDate") or entry.get("birth_date")),
            "is_active": entry.get("isActive", True),
            "vnr": _clean_string(entry.get("vnr") or entry.get("version")),
        }
        officers.append(officer)

    return officers


def _extract_activities(company_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_activities = company_payload.get("activities") or []
    activities: List[Dict[str, Any]] = []

    for entry in raw_activities:
        if not isinstance(entry, dict):
            continue
        activity = {
            "description": _clean_string(
                entry.get("description") or entry.get("text") or entry.get("activity")
            ),
            "is_active": entry.get("isActive", True),
            "vnr": _clean_string(entry.get("vnr") or entry.get("version")),
        }
        activities.append(activity)

    return activities


def _clean_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None


def _extract_candidate_fnr(candidate: Dict[str, Any]) -> Optional[str]:
    for key in ("fnr", "registerId", "register_id", "registerNumber", "register_number"):
        value = candidate.get(key)
        if value:
            return normalize_fn_number(str(value))
    return None


__all__ = [
    "FirmenbuchCompanyNotFound",
    "FirmenbuchFetchError",
    "fetch_company_profile_by_name_if_missing",
    "fetch_company_profile_if_missing",
]

