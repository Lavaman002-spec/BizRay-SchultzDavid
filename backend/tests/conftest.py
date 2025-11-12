"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
repo_root = backend_dir.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def backend_root():
    """Return the backend root directory."""
    return backend_dir


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI app."""
    from backend.services.api.main import app
    return TestClient(app)
