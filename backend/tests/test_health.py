# =============================================================================
# WORKFLOW — automated reproduction of Phase 1–2 HTTP checks
# =============================================================================
# RUN:  cd backend && PYTHONPATH=. python3 -m pytest tests/ -q
# Same URLs you can hit manually while uvicorn is running (see main.py header).
# MAP:  scripts/seed_demo_data.py PROJECT WORKFLOW MAP
# =============================================================================
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_telemetry_summary_shape():
    response = client.get("/telemetry/summary")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "reading_count",
        "quality_event_count",
        "first_reading_at",
        "last_reading_at",
        "data_sources",
    }
