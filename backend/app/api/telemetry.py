# =============================================================================
# WORKFLOW — Phase 2d: read persisted telemetry through HTTP
# =============================================================================
# Depends on: Phase 2a init_db, Phase 2b seed (or other ingest), models/plant_reading.py
# Called by:  main.py include_router
#
# CHECK after seed:
#   GET /telemetry/summary  →  reading_count, first/last timestamps, data_sources[]
#   Same query logic as this file lives in one place so UI and tests stay aligned.
# CHECK: GET /telemetry/summary, POST /telemetry/ingest-csv, POST /telemetry/quality/rescan
# =============================================================================
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PlantReading, QualityEvent
from app.schemas.telemetry import (
    IngestCsvResponse,
    QualityEventList,
    QualityEventOut,
    QualityRescanResponse,
    TelemetrySummary,
)
from app.services.csv_ingest import MEASURED_CSV_SOURCE, ingest_readings, readings_from_csv_text
from app.services.quality import scan_stored_readings

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


@router.get("/quality-events", response_model=QualityEventList)
def quality_events(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
) -> QualityEventList:
    rows = db.scalars(
        select(QualityEvent).order_by(QualityEvent.detected_at.desc()).limit(limit)
    ).all()
    events = [
        QualityEventOut(
            id=row.id,
            detected_at=row.detected_at,
            rule_code=row.rule_code,
            severity=row.severity,
            message=row.message,
        )
        for row in rows
    ]
    return QualityEventList(count=len(events), events=events)


@router.post("/ingest-csv", response_model=IngestCsvResponse)
async def ingest_csv(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> IngestCsvResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file")

    raw = (await file.read()).decode("utf-8")
    try:
        readings = readings_from_csv_text(raw)
        rows, events, skipped = ingest_readings(db, readings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if rows == 0 and skipped > 0:
        msg = f"No new rows ({skipped} timestamps already in database)."
    elif skipped > 0:
        msg = f"Inserted {rows} new rows; skipped {skipped} duplicate timestamps."
    else:
        msg = f"Inserted {rows} rows. Re-run offline train script to refresh forecasts."

    return IngestCsvResponse(
        rows_inserted=rows,
        rows_skipped_duplicates=skipped,
        quality_events_created=events,
        data_source=MEASURED_CSV_SOURCE,
        message=msg,
    )


@router.post("/quality/rescan", response_model=QualityRescanResponse)
def quality_rescan(db: Session = Depends(get_db)) -> QualityRescanResponse:
    db.execute(delete(QualityEvent))
    events = scan_stored_readings(db)
    db.add_all(events)
    db.commit()
    return QualityRescanResponse(
        quality_events_stored=len(events),
        message="Series quality rules re-applied to all plant_readings.",
    )
