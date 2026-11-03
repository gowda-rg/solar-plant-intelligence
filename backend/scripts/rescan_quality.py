#!/usr/bin/env python3
# WORKFLOW — re-run gap/stale rules on data already in PostgreSQL (no reseed)
# RUN: cd backend && PYTHONPATH=. python3 scripts/rescan_quality.py
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import delete

from app.database import get_session_factory  # noqa: E402
from app.models import QualityEvent  # noqa: E402
from app.services.quality import scan_stored_readings  # noqa: E402


def main() -> None:
    session = get_session_factory()()
    try:
        session.execute(delete(QualityEvent))
        events = scan_stored_readings(session)
        session.add_all(events)
        session.commit()
        print(f"Stored {len(events)} quality events after series scan.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
