from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_quality_events_list():
    response = client.get("/telemetry/quality-events?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "events" in body
    assert isinstance(body["events"], list)
