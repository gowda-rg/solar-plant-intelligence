# =============================================================================
# WORKFLOW — Phase 3 API tests (requires train script output)
# =============================================================================
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import forecast_artifacts

client = TestClient(app)


@pytest.fixture(scope="module")
def require_artifacts():
    if not (forecast_artifacts.artifacts_dir() / "metrics.json").is_file():
        pytest.skip("Run ml/train_forecast.py to generate artifacts")


def test_forecast_metrics(require_artifacts):
    response = client.get("/forecast/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "metrics" in body
    assert "mae_kw" in body["metrics"]
    assert body["train_rows"] > 0
    assert body["test_rows"] > 0


def test_forecast_evaluation(require_artifacts):
    response = client.get("/forecast/evaluation?limit=10")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] <= 10
    assert len(body["points"]) == body["count"]
    point = body["points"][0]
    assert {"measured_at", "actual_kw", "predicted_kw"}.issubset(point.keys())


def test_forecast_deviations(require_artifacts):
    response = client.get("/forecast/deviations")
    assert response.status_code == 200
    body = response.json()
    assert "days" in body
    assert len(body["days"]) > 0
    assert "summary" in body["days"][0]


def test_forecast_metrics_404_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(forecast_artifacts, "ARTIFACTS_DIR", tmp_path)
    response = client.get("/forecast/metrics")
    assert response.status_code == 404
