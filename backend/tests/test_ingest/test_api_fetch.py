"""Tests for the Firmenbuch fetch orchestration helpers."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from backend.services.ingest import api_fetch


class DummyClient:
    """Test helper implementing the Firmenbuch API client interface."""

    def __init__(
        self,
        payload: Any = None,
        *,
        error: Exception | None = None,
        search_results: List[Dict[str, Any]] | None = None,
        search_error: Exception | None = None,
    ) -> None:
        self.payload = payload
        self.error = error
        self.search_results = search_results or []
        self.search_error = search_error
        self.calls: List[str] = []
        self.search_calls: List[tuple[str, int]] = []

    def get_company_profile(self, register_id: str) -> Any:
        self.calls.append(register_id)
        if self.error:
            raise self.error
        return self.payload

    def search_companies(self, query: str, *, limit: int = 5) -> List[Dict[str, Any]]:
        self.search_calls.append((query, limit))
        if self.search_error:
            raise self.search_error
        return list(self.search_results)


def test_fetch_returns_existing_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """No API call should be made when the company is already cached."""

    cached = {"id": 1, "fnr": "123456A"}

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: cached,
    )

    dummy_client = DummyClient()

    result = api_fetch.fetch_company_profile_if_missing("FN 123456a", client=dummy_client)

    assert result == cached
    assert dummy_client.calls == []


def test_fetches_and_stores_company(monkeypatch: pytest.MonkeyPatch) -> None:
    """When missing locally the company is fetched, normalised, and stored."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    captured_args: Dict[str, Any] = {}

    def fake_create_company_with_relations(company_data: Dict[str, Any], **relations: Any) -> Dict[str, Any]:
        captured_args["company_data"] = company_data
        captured_args.update(relations)
        return {
            "id": 42,
            "fnr": company_data["fnr"],
            "name": company_data["name"],
            "legal_form": company_data.get("legal_form"),
            "state": company_data.get("state"),
            "city": company_data.get("city"),
            "officers": relations.get("officers", []),
            "addresses": relations.get("addresses", []),
            "activities": relations.get("activities", []),
        }

    monkeypatch.setattr(
        api_fetch.db_queries,
        "create_company_with_relations",
        fake_create_company_with_relations,
    )

    api_payload = {
        "registerId": "123456A",
        "name": "Example GmbH",
        "status": "active",
        "legalForm": {"code": "GES", "text": "Gesellschaft mit beschränkter Haftung"},
        "addresses": [
            {
                "street": "Ringstraße",
                "houseNumber": "1",
                "postalCode": "1010",
                "city": "Wien",
                "country": "Austria",
            }
        ],
        "officers": [
            {
                "title": "Mag.",
                "firstName": "Anna",
                "lastName": "Beispiel",
                "role": "Geschäftsführer",
                "birthDate": "1980-01-01",
            }
        ],
        "activities": [
            {"description": "IT Services", "isActive": True},
        ],
    }

    dummy_client = DummyClient(payload=api_payload)

    result = api_fetch.fetch_company_profile_if_missing("123456a", client=dummy_client)

    assert dummy_client.calls == ["123456A"]
    assert result["fnr"] == "123456A"
    assert result["addresses"][0]["city"] == "Wien"
    assert result["officers"][0]["full_name"]

    company_data = captured_args["company_data"]
    assert company_data["city"] == "Wien"
    assert company_data["state"] == "active"
    assert captured_args["addresses"][0]["street"] == "Ringstraße"
    assert captured_args["officers"][0]["role"] == "Geschäftsführer"
    assert captured_args["activities"][0]["description"] == "IT Services"


def test_fetch_uses_company_name_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads using alternative name keys should still populate the company name."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    captured_company: Dict[str, Any] = {}

    def fake_create_company_with_relations(company_data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        captured_company.update(company_data)
        return {"id": 1, **company_data}

    monkeypatch.setattr(
        api_fetch.db_queries,
        "create_company_with_relations",
        fake_create_company_with_relations,
    )

    api_payload = {
        "registerId": "654321B",
        "companyName": "Alias GmbH",
    }

    dummy_client = DummyClient(payload=api_payload)

    result = api_fetch.fetch_company_profile_if_missing("654321b", client=dummy_client)

    assert result["name"] == "Alias GmbH"
    assert captured_company["name"] == "Alias GmbH"


def test_fetch_extracts_name_from_firmenwortlaut(monkeypatch: pytest.MonkeyPatch) -> None:
    """Case-insensitive Firmenbuch keys with nested wrappers should produce a name."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    captured_company: Dict[str, Any] = {}

    def fake_create_company_with_relations(company_data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        captured_company.update(company_data)
        return {"id": 9, **company_data}

    monkeypatch.setattr(
        api_fetch.db_queries,
        "create_company_with_relations",
        fake_create_company_with_relations,
    )

    api_payload = {
        "company": {
            "registerId": "789012C",
            "firmenWortlaut": {"text": "Wrapper GmbH"},
        }
    }

    dummy_client = DummyClient(payload=api_payload)

    result = api_fetch.fetch_company_profile_if_missing("FN 789012c", client=dummy_client)

    assert result["name"] == "Wrapper GmbH"
    assert captured_company["name"] == "Wrapper GmbH"


def test_fetch_handles_company_list_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    """A list-wrapped company payload should still resolve the Firmenbuch name."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    captured_company: Dict[str, Any] = {}

    def fake_create_company_with_relations(company_data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        captured_company.update(company_data)
        return {"id": 11, **company_data}

    monkeypatch.setattr(
        api_fetch.db_queries,
        "create_company_with_relations",
        fake_create_company_with_relations,
    )

    api_payload = {
        "company": [
            {
                "registerId": "135790D",
                "firmenwortlaut": {"#text": "List Wrapper GmbH"},
            }
        ]
    }

    dummy_client = DummyClient(payload=api_payload)

    result = api_fetch.fetch_company_profile_if_missing("135790d", client=dummy_client)

    assert result["name"] == "List Wrapper GmbH"
    assert captured_company["name"] == "List Wrapper GmbH"


@pytest.mark.parametrize(
    "value",
    [
        "Case GmbH",
        {"text": "Case GmbH"},
        {"value": {"text": "Case GmbH"}},
        [{"name": "Case GmbH"}],
        {"#text": "Case GmbH"},
        {"@text": "Case GmbH"},
        {"$": "Case GmbH"},
        {"valueText": "Case GmbH"},
    ],
)
def test_extract_company_name_handles_wrappers(value: Any) -> None:
    """The helper should locate a string within nested wrappers regardless of case."""

    payload = {"firmenWortlaut": value}

    assert api_fetch._extract_company_name(payload) == "Case GmbH"


def test_extract_company_name_handles_company_list() -> None:
    """The company payload may be wrapped in a list before containing the name."""

    payload = {"company": [{"firmenwortlaut": {"#text": "List GmbH"}}]}

    assert api_fetch._extract_company_name(payload["company"]) == "List GmbH"
    assert api_fetch._extract_company_name(payload) == "List GmbH"


def test_fetch_company_suggestions_caches_profiles(monkeypatch: pytest.MonkeyPatch) -> None:
    """Suggestion lookups should fetch Firmenbuch profiles for discovered FNRs."""

    dummy_client = DummyClient(
        search_results=[
            {"registerId": "123456A", "name": "AEP-OBB GmbH"},
            {"registerId": "987654b", "companyName": {"text": "Other Wrapper GmbH"}},
        ]
    )

    captured_fnrs: List[str] = []

    def fake_fetch_company_profile_if_missing(
        fnr: str, *, client: Any | None = None
    ) -> Dict[str, Any]:
        captured_fnrs.append(fnr)
        assert client is dummy_client
        return {"fnr": fnr}

    monkeypatch.setattr(
        api_fetch,
        "fetch_company_profile_if_missing",
        fake_fetch_company_profile_if_missing,
    )

    suggestions = api_fetch.fetch_company_suggestions_from_firmenbuch(
        "obb", client=dummy_client, limit=3
    )

    assert suggestions == [
        {"name": "AEP-OBB GmbH", "fnr": "123456A"},
        {"name": "Other Wrapper GmbH", "fnr": "987654B"},
    ]
    assert captured_fnrs == ["123456A", "987654B"]


def test_fetch_company_suggestions_raises_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """No Firmenbuch matches should propagate a not-found error."""

    dummy_client = DummyClient(search_results=[])

    with pytest.raises(api_fetch.FirmenbuchCompanyNotFound):
        api_fetch.fetch_company_suggestions_from_firmenbuch("missing", client=dummy_client)


def test_fetch_company_suggestions_wraps_client_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client configuration issues should surface as fetch errors."""

    def failing_client() -> None:
        raise ValueError("missing base url")

    monkeypatch.setattr(api_fetch, "FirmenbuchAPIClient", failing_client)

    with pytest.raises(api_fetch.FirmenbuchFetchError) as excinfo:
        api_fetch.fetch_company_suggestions_from_firmenbuch("obb")

    assert "missing base url" in str(excinfo.value).lower()


def test_raises_when_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing record raises a descriptive error."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    dummy_client = DummyClient(payload=None)

    with pytest.raises(api_fetch.FirmenbuchCompanyNotFound):
        api_fetch.fetch_company_profile_if_missing("999999z", client=dummy_client)


def test_wraps_api_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """API layer exceptions are surfaced as fetch errors."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    dummy_client = DummyClient(error=api_fetch.FirmenbuchAPIError("Boom"))

    with pytest.raises(api_fetch.FirmenbuchFetchError):
        api_fetch.fetch_company_profile_if_missing("123456A", client=dummy_client)


def test_fetch_profile_wraps_client_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing Firmenbuch client configuration bubbles up as a fetch error."""

    monkeypatch.setattr(
        api_fetch.db_queries,
        "get_company_with_details_by_fnr",
        lambda _: None,
    )

    def failing_client() -> None:
        raise ValueError("configure base url")

    monkeypatch.setattr(api_fetch, "FirmenbuchAPIClient", failing_client)

    with pytest.raises(api_fetch.FirmenbuchFetchError) as excinfo:
        api_fetch.fetch_company_profile_if_missing("123456a")

    assert "base url" in str(excinfo.value).lower()


def test_fetch_by_name_prefers_exact_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """Searching by name should return the best matching candidate."""

    dummy_client = DummyClient(
        search_results=[
            {"fnr": "654321z", "name": "Other Company"},
            {"fnr": "123456A", "name": "Example GmbH"},
            {"registerId": "111111b", "name": "Example GmbH"},
        ]
    )

    captured: Dict[str, Any] = {}

    def fake_fetch(fnr: str, *, client: Any = None) -> Dict[str, Any]:
        captured["fnr"] = fnr
        assert client is dummy_client
        return {"fnr": fnr, "name": "Example GmbH"}

    monkeypatch.setattr(api_fetch, "fetch_company_profile_if_missing", fake_fetch)

    result = api_fetch.fetch_company_profile_by_name_if_missing(
        "Example GmbH", client=dummy_client
    )

    assert result == {"fnr": "123456A", "name": "Example GmbH"}
    assert captured["fnr"] == "123456A"
    assert dummy_client.search_calls == [("Example GmbH", 5)]


def test_fetch_by_name_skips_candidates_without_fnr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Candidates missing an FNR are ignored until a valid one is found."""

    dummy_client = DummyClient(
        search_results=[
            {"name": "No Number"},
            {"registerNumber": "654321x", "name": "Some Company"},
        ]
    )

    def fake_fetch(fnr: str, *, client: Any = None) -> Dict[str, Any]:
        return {"fnr": fnr}

    monkeypatch.setattr(api_fetch, "fetch_company_profile_if_missing", fake_fetch)

    result = api_fetch.fetch_company_profile_by_name_if_missing(
        "Some Company", client=dummy_client
    )

    assert result == {"fnr": "654321X"}


def test_fetch_by_name_handles_no_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty search result raises FirmenbuchCompanyNotFound."""

    dummy_client = DummyClient(search_results=[])

    with pytest.raises(api_fetch.FirmenbuchCompanyNotFound):
        api_fetch.fetch_company_profile_by_name_if_missing("Missing GmbH", client=dummy_client)


def test_fetch_by_name_wraps_search_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Errors from the search endpoint are wrapped consistently."""

    dummy_client = DummyClient(
        search_error=api_fetch.FirmenbuchAPIError("Boom"),
    )

    with pytest.raises(api_fetch.FirmenbuchFetchError):
        api_fetch.fetch_company_profile_by_name_if_missing("Example GmbH", client=dummy_client)


def test_fetch_by_name_wraps_client_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Misconfigured clients should raise consistent fetch errors for name lookups."""

    def failing_client() -> None:
        raise ValueError("set firmenbuch base url")

    monkeypatch.setattr(api_fetch, "FirmenbuchAPIClient", failing_client)

    with pytest.raises(api_fetch.FirmenbuchFetchError) as excinfo:
        api_fetch.fetch_company_profile_by_name_if_missing("Example GmbH")

    assert "firmenbuch" in str(excinfo.value).lower()
