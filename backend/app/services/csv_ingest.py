# =============================================================================
# WORKFLOW — shared CSV ingest logic for CLI script and POST /telemetry/ingest-csv
# Skips rows whose measured_at already exists (no duplicate inserts or spam events).
# =============================================================================
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PlantReading, QualityEvent
from app.services.quality import scan_reading_series, validate_batch

MEASURED_CSV_SOURCE = "MEASURED_CSV"


def parse_timestamp(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def readings_from_csv_text(text: str, data_source: str = MEASURED_CSV_SOURCE) -> list[PlantReading]:
    readings: list[PlantReading] = []
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "measured_at" not in reader.fieldnames or "power_kw" not in reader.fieldnames:
        raise ValueError("CSV must include columns: measured_at, power_kw")

    for row in reader:
        irr = row.get("irradiance_wm2") or row.get("irradiance")
        readings.append(
            PlantReading(
                measured_at=parse_timestamp(row["measured_at"]),
                power_kw=float(row["power_kw"]),
                irradiance_wm2=float(irr) if irr not in (None, "") else None,
                data_source=data_source,
            )
        )
    if not readings:
        raise ValueError("CSV contained no data rows")
    return readings


def filter_new_readings(session: Session, readings: list[PlantReading]) -> tuple[list[PlantReading], int]:
    timestamps = [r.measured_at for r in readings]
    existing = set(
        session.scalars(
            select(PlantReading.measured_at).where(PlantReading.measured_at.in_(timestamps))
        ).all()
    )
    new_rows = [r for r in readings if r.measured_at not in existing]
    skipped = len(readings) - len(new_rows)
    return new_rows, skipped


def ingest_readings(session: Session, readings: list[PlantReading]) -> tuple[int, int, int]:
    new_readings, skipped = filter_new_readings(session, readings)
    events: list[QualityEvent] = []

    if new_readings:
        events = validate_batch(session, new_readings)
        events.extend(scan_reading_series(new_readings))
        session.add_all(new_readings)

    if events:
        session.add_all(events)

    session.commit()
    return len(new_readings), len(events), skipped
