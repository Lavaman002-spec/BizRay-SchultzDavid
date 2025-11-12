"""Test main API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_root_endpoint(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "BizRay API is running"


def test_docs_endpoint(test_client):
    """Test that API docs are available."""
    response = test_client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint(test_client):
    """Test that OpenAPI schema is available."""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data