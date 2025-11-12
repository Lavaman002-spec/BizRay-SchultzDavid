"""Client for interacting with the Austrian Firmenbuch API."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

import requests

from shared.config import API_KEY, FIRMENBUCH_BASE_URL

logger = logging.getLogger(__name__)


class FirmenbuchAPIError(Exception):
    """Raised when the Firmenbuch API returns an error response."""


@dataclass
class FirmenbuchAPIClient:
    """Simple HTTP client for the Firmenbuch REST API."""

    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        self.base_url = (self.base_url or FIRMENBUCH_BASE_URL or "").rstrip("/")
        self.api_key = self.api_key or API_KEY

        if not self.base_url:
            raise ValueError(
                "FIRMENBUCH_BASE_URL environment variable must be configured to "
                "use the Firmenbuch API client."
            )

        if self.session is None:
            self.session = requests.Session()

    # -- Public API -----------------------------------------------------
    def get_company_profile(self, register_id: str) -> Optional[Dict[str, Any]]:
        """Return the company profile for the given Firmenbuch number."""

        if not register_id:
            raise ValueError("register_id must be provided")

        url = f"{self.base_url}/api/v1/company/{register_id}"
        headers = self._build_headers()

        logger.debug("Requesting Firmenbuch profile %s from %s", register_id, url)

        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:  # pragma: no cover - network errors are rare in tests
            raise FirmenbuchAPIError(f"Connection to Firmenbuch API failed: {exc}") from exc

        if response.status_code == 404:
            logger.info("Firmenbuch record %s not found", register_id)
            return None

        if response.status_code >= 400:
            raise FirmenbuchAPIError(
                f"Firmenbuch API returned HTTP {response.status_code}: {response.text}"
            )

        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - depends on remote API behaviour
            raise FirmenbuchAPIError("Firmenbuch API returned invalid JSON") from exc

        logger.debug(
            "Received Firmenbuch response for %s with status %s",
            register_id,
            response.status_code,
        )
        return payload

    def search_companies(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return Firmenbuch search matches for the provided query string."""

        query = (query or "").strip()
        if not query:
            raise ValueError("query must be provided")

        url = f"{self.base_url}/api/v1/search/company"
        headers = self._build_headers()
        params = {"q": query, "limit": limit}

        logger.debug("Searching Firmenbuch for '%s' via %s", query, url)

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network errors are rare in tests
            raise FirmenbuchAPIError(f"Connection to Firmenbuch API failed: {exc}") from exc

        if response.status_code >= 400:
            raise FirmenbuchAPIError(
                f"Firmenbuch API returned HTTP {response.status_code}: {response.text}"
            )

        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - depends on remote API behaviour
            raise FirmenbuchAPIError("Firmenbuch API returned invalid JSON") from exc

        if isinstance(payload, dict):
            results = payload.get("results") or payload.get("data") or []
        elif isinstance(payload, list):
            results = payload
        else:
            raise FirmenbuchAPIError(
                "Firmenbuch API search payload has unexpected format"
            )

        if not isinstance(results, list):
            raise FirmenbuchAPIError(
                "Firmenbuch API search results must be a list"
            )

        logger.debug(
            "Received %d Firmenbuch matches for query '%s'", len(results), query
        )
        return results

    # -- Internal helpers -----------------------------------------------
    def _build_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "bizray-backend/1.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


__all__ = [
    "FirmenbuchAPIClient",
    "FirmenbuchAPIError",
]

