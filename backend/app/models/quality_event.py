# SEMANTIC — data quality audit trail
# When ingest validation finds duplicates, gaps, or bad values, we store an event here
# instead of silently fixing data. Operators can trace *why* a row was flagged without
# a row was flagged without treating the score as a confirmed equipment fault.
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class QualityEvent(Base):
    __tablename__ = "quality_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rule_code: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="warning")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    plant_reading_id: Mapped[int | None] = mapped_column(
        ForeignKey("plant_readings.id", ondelete="SET NULL"), nullable=True
    )
