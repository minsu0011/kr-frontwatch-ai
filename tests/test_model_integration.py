"""Run with both requirements.txt and requirements-model.txt installed."""
import pytest
pytest.importorskip("sklearn")
pytest.importorskip("pyarrow")
from fastapi.testclient import TestClient
from app.main import app


def test_model_status_and_api_to_model_parity():
    with TestClient(app) as client:
        status = client.get("/api/internal/model-replay/status")
        assert status.status_code == 200
        assert status.json()["ready"] and len(status.json()["codes"]) == 12
        for code in status.json()["codes"]:
            response = client.get("/api/internal/model-replay/" + code)
            assert response.status_code == 200
            body = response.json()
            assert body["frozen_api_parity"]
            assert not body["live_inference_enabled"]
            assert not body["training_performed"]


def test_model_endpoint_rejects_non_capsule_and_bad_code():
    with TestClient(app) as client:
        assert client.get("/api/internal/model-replay/005930").status_code == 404
        assert client.get("/api/internal/model-replay/bad").status_code == 422
