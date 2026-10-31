# Project Status — Solar Plant Intelligence

**Last updated:** 2026-10-31  

## Current phase

**Phase 2 complete** — schema, synthetic seed, `/telemetry/summary`.  
**Next:** Phase 3 — `ml/train_forecast.py` (chronological split, metrics JSON).

## Reproduce and verify (by phase)

All commands assume `cd backend` and `backend/.env` is set.

| Phase | What you prove | Run | Where to check |
|-------|----------------|-----|----------------|
| **1** | API reaches PostgreSQL | `PYTHONPATH=. python3 -m pytest tests/test_health.py -q` | Tests pass; or `uvicorn app.main:app --reload --port 8000` → `/health/db` |
| **2a** | Tables exist | `PYTHONPATH=. python3 scripts/init_db.py` | `psql` → `\dt` shows `plant_readings`, `quality_events` |
| **2b** | Demo data loaded | `PYTHONPATH=. python3 scripts/seed_demo_data.py` | Terminal: `Inserted 336 readings…` or `Skip seed` if already loaded |
| **2c–d** | Read path works | `PYTHONPATH=. python3 -m pytest tests/ -q` | `/telemetry/summary` → `reading_count` ≈ 336, `SYNTHETIC_DEMO` |
| **3** | *(planned)* | `ml/train_forecast.py` | `ml/artifacts/metrics.json` + new API routes |
| **4** | *(planned)* | `frontend/` dev server | Charts match API JSON |

**Master map in code:** open `backend/scripts/seed_demo_data.py` — top **PROJECT WORKFLOW MAP** block links every file and check.

**Reset demo data (optional):** in psql, `TRUNCATE quality_events, plant_readings;` then re-run seed script.

## Reading order (slow walkthrough)

1. `scripts/seed_demo_data.py` (workflow map + ingest story)  
2. `scripts/init_db.py` → `app/models/plant_reading.py`  
3. `app/services/quality.py` → `app/api/telemetry.py` → `app/main.py`  
4. `app/database.py` + `app/config.py` when tracing connections  

## Next actions

1. Add `ml/train_forecast.py` with the same WORKFLOW header style  
2. API routes for forecast + metrics artifact  
3. React dashboard (Phase 4)  
