"""
Pytest configuration and fixtures for DocGuard tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_code():
    """Sample Python code with issues."""
    return """
import pandas as pd
import requests

def get_data():
    SELECT * FROM fake_table
    DELETE FROM users
    return data
"""

@pytest.fixture
def sample_doc():
    """Sample documentation with issues."""
    return """
# Old System

This uses the old_api and legacy endpoints.
"""