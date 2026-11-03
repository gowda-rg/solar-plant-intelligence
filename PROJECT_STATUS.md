# Project Status — Solar Plant Intelligence

**Last updated:** 2026-11-03  

## Current phase

**MVP+** — quality gap/stale detection, daily forecast deviation narratives, CSV ingest path, UI panels.

## Refresh demo after these changes (important)

Existing DB may lack injected defects and old artifacts lack `daily_deviations.json`:

```bash
cd backend
# psql or SQL: TRUNCATE quality_events, plant_readings;
PYTHONPATH=. python3 scripts/seed_demo_data.py
PYTHONPATH=. python3 ../ml/train_forecast.py
PYTHONPATH=. python3 scripts/rescan_quality.py   # only if you did NOT reseed but want events
PYTHONPATH=. python3 -m pytest tests/ -q
```

Optional measured CSV (small example in repo):

```bash
PYTHONPATH=. python3 scripts/ingest_csv.py ../data/raw/example_plant_export.csv
```

## Full stack run

```bash
# backend + train (above), then:
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
cd ../frontend && npm run dev
```

## New endpoints / UI

| Piece | Check |
|-------|--------|
| `GET /telemetry/quality-events` | UI “Data quality events” panel |
| `GET /forecast/deviations` | UI “Day-level forecast deviation” |
| `ml/artifacts/daily_deviations.json` | Matches API |
| `scripts/ingest_csv.py` | Adds `MEASURED_CSV` source |

| `POST /telemetry/ingest-csv` | Engineering lab — skips duplicate timestamps |
| `POST /telemetry/quality/rescan` | Engineering lab — Re-scan quality |
| Pipeline inspection (on demand) | `frontend/src/components/PipelineInspect.tsx` |

Demo walkthrough (text + mermaid, no recording): `docs/DEMO_FLOW.md`

## Walkthrough beats (technical)

1. Ingest + **series** quality (gap, stale) — not confirmed faults  
2. Chronological ML + **daily deviation copy** for operators  
3. Optional **CSV ingest** with separate `data_source` label (duplicates skipped)  
4. Operator-first UI; optional pipeline inspection and engineering lab actions  
