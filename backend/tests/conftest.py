"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def backend_root():
    """Return the backend root directory."""
    return backend_dir


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI app."""
    from services.api.main import app
    return TestClient(app)
