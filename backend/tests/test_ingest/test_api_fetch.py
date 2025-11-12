"""Tests for the Firmenbuch fetch orchestration helpers."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from services.ingest import api_fetch


class DummyClient:
    """Test helper implementing the Firmenbuch API client interface."""

    def __init__(self, payload: Any = None, *, error: Exception | None = None):
        self.payload = payload
        self.error = error
        self.calls: List[str] = []

    def get_company_profile(self, register_id: str) -> Any:
        self.calls.append(register_id)
        if self.error:
            raise self.error
        return self.payload


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
