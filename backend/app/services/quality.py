# =============================================================================
# WORKFLOW — Phase 2c: ingest-time + series scan data quality
# =============================================================================
# validate_batch: per-row checks on an incoming batch
# scan_reading_series: ordered timeline checks (gaps, stale/flatline during daylight)
# NOT equipment fault confirmation — analytical flags for operator review
# MAP: scripts/seed_demo_data.py PROJECT WORKFLOW MAP
# =============================================================================
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PlantReading, QualityEvent

RULE_DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
RULE_NEGATIVE_POWER = "NEGATIVE_POWER"
RULE_COLLECTION_GAP = "COLLECTION_GAP"
RULE_STALE_SENSOR = "STALE_SENSOR"

EXPECTED_STEP = timedelta(hours=1)
GAP_TOLERANCE = timedelta(minutes=90)
STALE_REPEAT_COUNT = 3
STALE_MIN_POWER_KW = 0.3


def validate_batch(session: Session, readings: list[PlantReading]) -> list[QualityEvent]:
    events: list[QualityEvent] = []
    now = datetime.now(timezone.utc)
    seen_timestamps: set[datetime] = set()

    for reading in readings:
        if reading.measured_at in seen_timestamps:
            events.append(
                QualityEvent(
                    detected_at=now,
                    rule_code=RULE_DUPLICATE_TIMESTAMP,
                    severity="error",
                    message=f"Duplicate timestamp in batch: {reading.measured_at.isoformat()}",
                )
            )
        seen_timestamps.add(reading.measured_at)

        if reading.power_kw < 0:
            events.append(
                QualityEvent(
                    detected_at=now,
                    rule_code=RULE_NEGATIVE_POWER,
                    severity="error",
                    message=f"Negative power_kw={reading.power_kw} at {reading.measured_at.isoformat()}",
                    plant_reading_id=None,
                )
            )

    if readings:
        timestamps = [r.measured_at for r in readings]
        existing = session.scalars(
            select(PlantReading.measured_at).where(PlantReading.measured_at.in_(timestamps))
        ).all()
        for ts in existing:
            events.append(
                QualityEvent(
                    detected_at=now,
                    rule_code=RULE_DUPLICATE_TIMESTAMP,
                    severity="warning",
                    message=f"Timestamp already in database: {ts.isoformat()}",
                )
            )

    return events


def scan_reading_series(readings: list[PlantReading]) -> list[QualityEvent]:
    """Detect collection gaps and flatlined daylight output on a sorted series."""
    if len(readings) < 2:
        return []

    ordered = sorted(readings, key=lambda r: r.measured_at)
    now = datetime.now(timezone.utc)
    events: list[QualityEvent] = []

    for prev, curr in zip(ordered, ordered[1:]):
        delta = curr.measured_at - prev.measured_at
        if delta > EXPECTED_STEP + GAP_TOLERANCE:
            missing_hours = int(delta.total_seconds() // 3600) - 1
            events.append(
                QualityEvent(
                    detected_at=now,
                    rule_code=RULE_COLLECTION_GAP,
                    severity="warning",
                    message=(
                        f"Collection gap ~{missing_hours}h between "
                        f"{prev.measured_at.isoformat()} and {curr.measured_at.isoformat()}"
                    ),
                )
            )

    run_length = 1
    for idx in range(1, len(ordered)):
        prev_r = ordered[idx - 1]
        curr_r = ordered[idx]
        same_power = abs(curr_r.power_kw - prev_r.power_kw) < 1e-6
        daylight = 6 <= curr_r.measured_at.hour <= 18 and curr_r.power_kw >= STALE_MIN_POWER_KW
        if same_power and daylight:
            run_length += 1
        else:
            run_length = 1
        if run_length == STALE_REPEAT_COUNT:
            events.append(
                QualityEvent(
                    detected_at=now,
                    rule_code=RULE_STALE_SENSOR,
                    severity="warning",
                    message=(
                        f"Stale/flat output {curr_r.power_kw} kW for {run_length} hourly samples "
                        f"ending {curr_r.measured_at.isoformat()} (check sensor or comms)"
                    ),
                )
            )

    return events


def scan_stored_readings(session: Session) -> list[QualityEvent]:
    """Re-run series rules on all rows already in PostgreSQL (maintenance script / reseed)."""
    readings = list(
        session.scalars(select(PlantReading).order_by(PlantReading.measured_at)).all()
    )
    return scan_reading_series(readings)
