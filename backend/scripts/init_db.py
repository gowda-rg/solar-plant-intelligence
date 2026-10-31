#!/usr/bin/env python3
# =============================================================================
# WORKFLOW — Phase 2a: create empty PostgreSQL tables from ORM models
# =============================================================================
# Runs BEFORE seed_demo_data.py (Phase 2b).
#
# INPUT:  Model classes on app.models.Base (plant_readings, quality_events)
# OUTPUT: Tables in PostgreSQL (safe to run again — skips existing tables)
#
# RUN:    cd backend && PYTHONPATH=. python3 scripts/init_db.py
# CHECK:  psql … -c "\dt"  →  plant_readings, quality_events listed
# NEXT:   scripts/seed_demo_data.py (see its PROJECT WORKFLOW MAP)
# =============================================================================
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import create_schema, get_engine  # noqa: E402


def main() -> None:
    create_schema(get_engine())
    print("Schema created (create_all is idempotent for existing tables).")


if __name__ == "__main__":
    main()
