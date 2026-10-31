# =============================================================================
# WORKFLOW — Phase 2d: read persisted telemetry through HTTP
# =============================================================================
# Depends on: Phase 2a init_db, Phase 2b seed (or other ingest), models/plant_reading.py
# Called by:  main.py include_router
#
# CHECK after seed:
#   GET /telemetry/summary  →  reading_count, first/last timestamps, data_sources[]
#   Same query logic as this file lives in one place so UI and tests stay aligned.
# MAP: scripts/seed_demo_data.py PROJECT WORKFLOW MAP
# =============================================================================
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PlantReading, QualityEvent
from app.schemas.telemetry import TelemetrySummary

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/summary", response_model=TelemetrySummary)
def telemetry_summary(db: Session = Depends(get_db)) -> TelemetrySummary:
    reading_count = db.scalar(select(func.count()).select_from(PlantReading)) or 0
    quality_event_count = db.scalar(select(func.count()).select_from(QualityEvent)) or 0

    bounds = db.execute(
        select(func.min(PlantReading.measured_at), func.max(PlantReading.measured_at))
    ).one()
    first_reading_at, last_reading_at = bounds

    sources = db.scalars(select(PlantReading.data_source).distinct()).all()

    return TelemetrySummary(
        reading_count=reading_count,
        quality_event_count=quality_event_count,
        first_reading_at=first_reading_at,
        last_reading_at=last_reading_at,
        data_sources=sorted(sources),
    )
