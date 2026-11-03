#!/usr/bin/env python3
# WORKFLOW — CLI wrapper; UI uses POST /telemetry/ingest-csv with same service layer
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database import create_schema, get_session_factory  # noqa: E402
from app.services.csv_ingest import ingest_readings, readings_from_csv_text  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: ingest_csv.py path/to/file.csv")

    csv_path = Path(sys.argv[1]).resolve()
    create_schema()
    text = csv_path.read_text(encoding="utf-8")
    readings = readings_from_csv_text(text)
    session = get_session_factory()()
    try:
        row_count, event_count, skipped = ingest_readings(session, readings)
        print(
            f"Ingested {row_count} rows, skipped {skipped} duplicates, "
            f"{event_count} quality events."
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
