# =============================================================================
# WORKFLOW — Phase 2c: ingest-time data quality (not forecast / ML anomalies)
# =============================================================================
# Called from: scripts/seed_demo_data.py (and future CSV ingest scripts)
# INPUT:       List of PlantReading about to be inserted
# OUTPUT:      QualityEvent rows explaining rule hits (stored alongside readings)
# CHECK:       After seed, SELECT count(*) FROM quality_events; (demo batch often 0)
# NOTE:        Forecast residuals and operator alarms come later in ml/ + API.
# MAP:         scripts/seed_demo_data.py PROJECT WORKFLOW MAP
# =============================================================================
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PlantReading, QualityEvent

RULE_DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
RULE_NEGATIVE_POWER = "NEGATIVE_POWER"


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
