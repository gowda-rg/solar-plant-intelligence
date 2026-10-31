# SEMANTIC — API response shapes (Pydantic)
# Separates what clients see from SQLAlchemy ORM internals — keeps /docs accurate for frontend work.
from datetime import datetime

from pydantic import BaseModel


class TelemetrySummary(BaseModel):
    reading_count: int
    quality_event_count: int
    first_reading_at: datetime | None
    last_reading_at: datetime | None
    data_sources: list[str]
