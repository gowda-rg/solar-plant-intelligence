# SEMANTIC — API response shapes (Pydantic)
# Separates what clients see from SQLAlchemy ORM internals — keeps /docs accurate for frontend work.
from datetime import datetime

from pydantic import BaseModel, Field


class TelemetrySummary(BaseModel):
    reading_count: int
    quality_event_count: int
    first_reading_at: datetime | None
    last_reading_at: datetime | None
    data_sources: list[str]


class QualityEventOut(BaseModel):
    id: int
    detected_at: datetime
    rule_code: str
    severity: str
    message: str


class QualityEventList(BaseModel):
    count: int
    events: list[QualityEventOut]


class IngestCsvResponse(BaseModel):
    rows_inserted: int
    rows_skipped_duplicates: int
    quality_events_created: int
    data_source: str
    message: str


class QualityRescanResponse(BaseModel):
    quality_events_stored: int
    message: str
