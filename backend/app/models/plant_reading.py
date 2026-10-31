# =============================================================================
# WORKFLOW — Phase 2 table: one row = one plant measurement at measured_at
# =============================================================================
# Columns power_kw / irradiance_wm2 feed Phase 3 feature engineering (ml/).
# data_source must stay honest (SYNTHETIC_DEMO vs future MEASURED_* CSV ingest).
# Created by init_db.py; rows inserted by seed_demo_data.py or future ingest.
# =============================================================================
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PlantReading(Base):
    __tablename__ = "plant_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    irradiance_wm2: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_source: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("ix_plant_readings_measured_at", "measured_at"),
        Index("ix_plant_readings_data_source", "data_source"),
    )
