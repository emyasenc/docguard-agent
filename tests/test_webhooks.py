"""
Tests for the webhook endpoints.
"""

import os
os.environ["TESTING"] = "true"

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "DocGuard" in data["service"]

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "DocGuard"
    assert data["status"] == "operational"

def test_webhook_ignores_non_pr_events():
    """Test that non-PR events are ignored."""
    payload = {"action": "push"}
    response = client.post(
        "/webhooks/github",
        json=payload,
        headers={"X-GitHub-Event": "push"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ignored"