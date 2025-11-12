"""Tests for the search API router."""

from services.api.routers import search as search_router


def test_search_fallback_fetches_missing_company(monkeypatch, test_client):
    """When a Firmenbuch number is missing locally, the API should fetch it on demand."""

    search_calls = []

    def fake_search_companies(query: str, limit: int, offset: int):
        search_calls.append(query)
        return [], 0

    def fake_fetch_company(fnr: str):
        assert fnr == "123456A"
        return {"fnr": fnr}

    def fake_get_company(fnr: str):
        return {
            "id": 42,
            "fnr": fnr,
            "name": "Fetched Company",
            "addresses": [],
            "officers": [],
            "activities": [],
        }

    monkeypatch.setattr(search_router.db_queries, "search_companies", fake_search_companies)
    monkeypatch.setattr(search_router, "fetch_company_profile_if_missing", fake_fetch_company)
    monkeypatch.setattr(search_router.db_queries, "get_company_with_details_by_fnr", fake_get_company)

    response = test_client.get("/api/search/?query=FN%20123456a")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["count"] == 1
    assert payload["results"][0]["fnr"] == "123456A"
    assert payload["results"][0]["name"] == "Fetched Company"
    assert search_calls == ["FN 123456a"]


def test_search_fallback_handles_missing_remote_record(monkeypatch, test_client):
    """If the Firmenbuch API does not know the record, keep search results empty."""

    fetch_calls = []

    def fake_search_companies(query: str, limit: int, offset: int):
        return [], 0

    def fake_fetch_company(fnr: str):
        fetch_calls.append(fnr)
        raise search_router.FirmenbuchCompanyNotFound

    monkeypatch.setattr(search_router.db_queries, "search_companies", fake_search_companies)
    monkeypatch.setattr(search_router, "fetch_company_profile_if_missing", fake_fetch_company)

    response = test_client.get("/api/search/?query=123456a")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 0
    assert payload["count"] == 0
    assert payload["results"] == []
    assert fetch_calls == ["123456A"]


def test_search_name_fallback_fetches_missing_company(monkeypatch, test_client):
    """When searching by name, missing companies should be pulled from Firmenbuch."""

    def fake_search_companies(query: str, limit: int, offset: int):
        assert query == "Example GmbH"
        return [], 0

    def fake_fetch_by_name(name: str):
        assert name == "Example GmbH"
        return {
            "id": 7,
            "fnr": "123456A",
            "name": "Example GmbH",
            "addresses": [],
            "officers": [],
            "activities": [],
        }

    def fake_get_company(fnr: str):
        assert fnr == "123456A"
        return {
            "id": 7,
            "fnr": fnr,
            "name": "Example GmbH",
            "addresses": [],
            "officers": [],
            "activities": [],
        }

    monkeypatch.setattr(search_router.db_queries, "search_companies", fake_search_companies)
    monkeypatch.setattr(
        search_router,
        "fetch_company_profile_by_name_if_missing",
        fake_fetch_by_name,
    )
    monkeypatch.setattr(search_router.db_queries, "get_company_with_details_by_fnr", fake_get_company)

    response = test_client.get("/api/search/?query=Example%20GmbH")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["count"] == 1
    assert payload["results"][0]["fnr"] == "123456A"
    assert payload["results"][0]["name"] == "Example GmbH"


def test_search_name_fallback_handles_missing_remote_record(monkeypatch, test_client):
    """If Firmenbuch search finds nothing, keep the response empty."""

    def fake_search_companies(query: str, limit: int, offset: int):
        return [], 0

    def fake_fetch_by_name(name: str):
        raise search_router.FirmenbuchCompanyNotFound

    monkeypatch.setattr(search_router.db_queries, "search_companies", fake_search_companies)
    monkeypatch.setattr(
        search_router,
        "fetch_company_profile_by_name_if_missing",
        fake_fetch_by_name,
    )

    response = test_client.get("/api/search/?query=Unknown%20GmbH")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 0
    assert payload["count"] == 0
    assert payload["results"] == []
