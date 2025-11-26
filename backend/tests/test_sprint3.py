import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from backend.services.api.main import app
from backend.services.api.dependencies import get_current_user, get_db

client = TestClient(app)

# Mock User
mock_user = MagicMock()
mock_user.id = "test-user-id"
mock_user.email = "test@example.com"

# Mock DB
mock_db = MagicMock()

async def override_get_current_user():
    return mock_user

def override_get_db():
    return mock_db

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

def test_auth_me():
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["id"] == "test-user-id"

def test_get_watchlist():
    # Mock response
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"company_id": 1}]
    
    response = client.get("/api/watchlist/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["company_id"] == 1

def test_add_to_watchlist():
    # Mock company check
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]
    # Mock insert
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1, "company_id": 1}]
    
    response = client.post("/api/watchlist/1")
    assert response.status_code == 200
    assert response.json()["company_id"] == 1

def test_get_graph():
    # Mock company fetch
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1, "name": "Test Corp"}]
    # Mock officers fetch (need to reset mock to handle sequential calls or use side_effect)
    # For simplicity, we assume the same mock object is returned and we just check structure
    
    # A better way is to mock specific chains, but with MagicMock it's tricky for chained calls.
    # We'll just check if the endpoint returns 200 and correct structure given the mocks.
    
    response = client.get("/api/graph/1")
    assert response.status_code == 200
    data = response.json()
    assert "elements" in data
    assert len(data["elements"]) > 0
    assert data["elements"][0]["data"]["id"] == "c_1"

def test_get_stats():
    # Mock stats query
    # Since get_dashboard_stats uses multiple queries, we need to mock the return value of the function directly
    # or mock the db calls. Mocking the function is easier here.
    with patch("backend.database.queries.get_dashboard_stats") as mock_stats:
        mock_stats.return_value = {
            "total_companies": 100,
            "active_companies": 50,
            "total_officers": 200
        }
        response = client.get("/api/stats/")
        assert response.status_code == 200
        assert response.json() == {
            "total_companies": 100,
            "active_companies": 50,
            "total_officers": 200
        }
