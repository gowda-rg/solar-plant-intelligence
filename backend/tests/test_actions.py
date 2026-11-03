import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_CSV = """measured_at,power_kw,irradiance_wm2
2099-06-15T10:00:00+00:00,2.5,600
2099-06-15T11:00:00+00:00,3.1,700
"""


def test_ingest_csv_upload():
    response = client.post(
        "/telemetry/ingest-csv",
        files={"file": ("test_upload.csv", io.BytesIO(SAMPLE_CSV.encode()), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rows_inserted"] == 2
    assert body["data_source"] == "MEASURED_CSV"

    again = client.post(
        "/telemetry/ingest-csv",
        files={"file": ("test_upload.csv", io.BytesIO(SAMPLE_CSV.encode()), "text/csv")},
    )
    assert again.status_code == 200
    body2 = again.json()
    assert body2["rows_inserted"] == 0
    assert body2["rows_skipped_duplicates"] == 2


def test_quality_rescan():
    response = client.post("/telemetry/quality/rescan")
    assert response.status_code == 200
    assert "quality_events_stored" in response.json()
