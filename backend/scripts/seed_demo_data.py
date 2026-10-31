#!/usr/bin/env python3

# =============================================================================
# PROJECT WORKFLOW MAP — start here to see how the backend pieces connect
# =============================================================================
#
# Phase 1 — API ↔ PostgreSQL (connectivity only)
#   Files:  app/config.py → app/database.py → app/main.py (/health, /health/db)
#   Run:    cd backend
#           PYTHONPATH=. python3 -m pytest tests/test_health.py -q
#           PYTHONPATH=. uvicorn app.main:app --reload --port 8000
#   Check:  http://127.0.0.1:8000/health/db  →  database "connected"
#           OpenAPI docs: http://127.0.0.1:8000/docs
#
# Phase 2 — Schema → demo ingest → read API  (this script is step 2b)
#   Order:  app/models/*.py          (row shapes)
#           scripts/init_db.py       (step 2a — create tables)
#           scripts/seed_demo_data.py (step 2b — insert SYNTHETIC_DEMO) ← YOU ARE HERE
#           app/services/quality.py  (step 2c — rules during ingest)
#           app/api/telemetry.py     (step 2d — GET /telemetry/summary)
#           app/main.py              (registers telemetry routes)
#   Run:    PYTHONPATH=. python3 scripts/init_db.py
#           PYTHONPATH=. python3 scripts/seed_demo_data.py
#           PYTHONPATH=. python3 -m pytest tests/ -q
#   Check:  http://127.0.0.1:8000/telemetry/summary
#           Expect reading_count ≈ 336, data_sources includes "SYNTHETIC_DEMO"
#   SQL:    psql $DATABASE_URL -c "SELECT count(*), data_source FROM plant_readings GROUP BY 2;"
#
#   Re-run seed from scratch (only when learning / debugging ingest):
#     TRUNCATE quality_events, plant_readings; then run this script again.
#
# Phase 3 — Forecasting (next build step — not in repo yet)
#   Planned: ml/train_forecast.py → ml/artifacts/metrics.json → API → frontend/
#   Reproduce steps will live in that script header when added.
#
# Phase 4 — Dashboard (after Phase 3)
#   Planned: frontend/ calls API; charts show only backend JSON (traceable numbers).
# =============================================================================
#
# THIS SCRIPT — INPUT / OUTPUT / LABEL
#   INPUT:   Nothing on disk; readings built in memory (see build_readings).
#   OUTPUT:  Rows in plant_readings; optional rows in quality_events.
#   LABEL:   Every row uses data_source = SYNTHETIC_DEMO (not real SCADA).
#
# HOW TO RUN:
#   cd backend && PYTHONPATH=. python3 scripts/seed_demo_data.py
# =============================================================================

import math
import sys

from datetime import datetime, timedelta, timezone
from pathlib import Path


# Find the main backend directory so Python can locate the application modules.
BACKEND_ROOT = Path(__file__).resolve().parents[1]

# Add the backend directory to Python's import path if it is not already present.
# This allows the script to import the database, models, and services.
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# Import SQLAlchemy functions used to interact with the database.
from sqlalchemy import func, select

# Import the functions responsible for creating the database schema
# and establishing database sessions.
from app.database import create_schema, get_session_factory  # noqa: E402

# Import the database models.
# PlantReading stores solar plant measurements.
# QualityEvent stores issues identified during data validation.
from app.models import PlantReading, QualityEvent  # noqa: E402

# Import the validation service.
# It checks the generated readings against the application's
# predefined data quality rules.
from app.services.quality import validate_batch  # noqa: E402


# Identify all generated records as synthetic demonstration data.
# This helps distinguish simulated readings from real production data.
DATA_SOURCE = "SYNTHETIC_DEMO"

# Generate 14 days of hourly readings.
# 24 hours multiplied by 14 days gives 336 readings.
HOURS = 24 * 14


def _synthetic_power_kw(hour_of_day: float, day_index: int) -> float:
    """
    Generate simulated solar power output for a particular hour.

    Solar power is assumed to be zero during nighttime.
    During daylight hours, power gradually increases toward midday
    and decreases again toward the evening.

    A mathematical bell-shaped curve is used to create
    a realistic-looking daily solar production pattern.

    NOTE:
    This is a simplified simulation, not a scientifically
    accurate physical model of solar power generation.
    """

    # Assume there is no solar power generation before 6 AM
    # or after 6 PM.
    if hour_of_day < 6 or hour_of_day > 18:
        return 0.0

    # Calculate how far the current hour is from solar noon (12 PM).
    # This value controls the shape of the solar production curve.
    x = (hour_of_day - 12) / 6

    # Set the approximate maximum power output to 4.5 kW.
    # A small sine-based variation is added to make different
    # days slightly different from one another.
    peak = 4.5 + 0.1 * math.sin(day_index / 3)

    # Apply a Gaussian bell curve to simulate solar generation.
    # The output is highest around midday and decreases
    # toward sunrise and sunset.
    #
    # max(0.0, ...) ensures that generated power never becomes negative.
    return max(0.0, peak * math.exp(-0.5 * x * x))


def build_readings() -> list[PlantReading]:
    """
    Create the complete set of simulated solar plant readings.

    The function generates one reading for every hour
    across the previous 14 days.

    Each reading contains:
    - Measurement timestamp
    - Simulated power output in kilowatts
    - Simulated solar irradiance in watts per square metre
    - Data source identifying it as synthetic data

    The generated records are returned as a list.
    """

    # Determine the starting timestamp.
    # Use the current UTC time, rounded down to the beginning
    # of the current hour, and move back 14 days.
    start = datetime.now(timezone.utc).replace(
        minute=0,
        second=0,
        microsecond=0
    ) - timedelta(hours=HOURS)

    # Create an empty list to temporarily hold generated readings.
    readings: list[PlantReading] = []

    # Generate one measurement for every hour in the 14-day period.
    for i in range(HOURS):

        # Calculate the timestamp corresponding to the current iteration.
        ts = start + timedelta(hours=i)

        # Extract the hour of the day.
        # This value is used to calculate solar power output.
        hour = ts.hour + ts.minute / 60

        # Estimate solar irradiance using the simulated power output.
        #
        # Irradiance is set to None during nighttime because
        # the simulation does not generate daylight measurements then.
        #
        # During daylight, irradiance is scaled relative to
        # the approximate maximum power output of 4.5 kW.
        irr = (
            None
            if ts.hour < 6 or ts.hour > 18
            else 800 * _synthetic_power_kw(hour, i // 24) / 4.5
        )

        # Create a PlantReading database object.
        # This object represents one hourly measurement
        # from the simulated solar power plant.
        readings.append(
            PlantReading(
                measured_at=ts,

                # Store the simulated solar power output in kilowatts.
                power_kw=_synthetic_power_kw(hour, i // 24),

                # Store the estimated solar irradiance.
                irradiance_wm2=irr,

                # Clearly identify the record as generated demo data.
                data_source=DATA_SOURCE,
            )
        )

    # Return all 336 generated measurement records.
    return readings


def main() -> None:
    """
    Main execution function.

    This function handles the complete demo data seeding process:

    1. Create the database schema if required.
    2. Establish a database connection.
    3. Check whether readings already exist.
    4. Generate synthetic solar readings.
    5. Validate the generated data.
    6. Save readings and quality events.
    7. Commit the transaction.
    8. Close the database session.
    """

    # Make sure the required database tables exist before inserting data.
    create_schema()

    # Create a database session.
    # A session allows the script to read and write database records.
    session = get_session_factory()()

    try:

        # Check how many solar readings are already stored in the database.
        # This prevents the script from repeatedly inserting
        # the same demonstration dataset.
        existing = session.scalar(
            select(func.count()).select_from(PlantReading)
        ) or 0

        # If at least one reading already exists, skip the seeding process.
        if existing > 0:
            print(f"Skip seed: {existing} readings already present.")
            return

        # Generate two weeks of synthetic hourly solar measurements.
        readings = build_readings()

        # Send the generated readings through the application's
        # data quality validation service.
        #
        # The validation service checks whether the readings
        # satisfy the predefined quality rules.
        #
        # If any rules are triggered, corresponding QualityEvent
        # records are returned.
        events = validate_batch(session, readings)

        # Add all generated solar readings to the database session.
        session.add_all(readings)

        # Add any quality events identified during validation.
        session.add_all(events)

        # Permanently save all pending database changes.
        session.commit()

        # Display a summary showing how many readings and quality events
        # were successfully inserted.
        print(
            f"Inserted {len(readings)} readings "
            f"({DATA_SOURCE}), {len(events)} quality events."
        )

    finally:

        # Always close the database session, even if an error occurs
        # or the script exits early.
        session.close()


# This condition ensures that main() runs only when this file
# is executed directly, rather than when it is imported by another module.
if __name__ == "__main__":
    main()
