"""Integration-style tests for the FastAPI routes (uses TestClient, mocks services)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Patch heavy services before importing the app
    with (
        patch("app.services.reranker.get_reranker") as mock_reranker,
        patch("app.services.confluence.get_confluence_client") as mock_confluence,
    ):
        reranker_inst = MagicMock()
        reranker_inst.loaded = True
        reranker_inst.rerank.return_value = []
        mock_reranker.return_value = reranker_inst

        confluence_inst = MagicMock()
        confluence_inst.health_check = AsyncMock(return_value=True)
        confluence_inst.search = AsyncMock(return_value=[])
        mock_confluence.return_value = confluence_inst

        from app.main import app
        yield TestClient(app)


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "confluence_reachable" in data
    assert "reranker_loaded" in data
