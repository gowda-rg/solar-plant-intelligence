# Development notes (semantic checkpoints)

Short explanations of what each milestone *means* in the system—not step-by-step tutorials.

## Phase 1 — API can reach PostgreSQL

**What enters:** HTTP GET `/health/db`  
**What happens:** FastAPI loads `DATABASE_URL` from `backend/.env`, SQLAlchemy opens a connection, runs `SELECT 1`.  
**What exits:** JSON `{ "status": "ok", "database": "connected" }` or HTTP 503 if the DB is down or credentials fail.  
**Why it matters:** Every later feature (telemetry rows, forecasts) assumes this path works; fail fast here instead of debugging ingest later.  
**How to verify:** `pytest backend/tests/test_health.py` from a venv with dependencies installed.

## Phase 2 — Ingest (planned)

Raw CSV → validated rows in PostgreSQL tables. Quality rules run at ingest time.

## Phase 3 — Offline ML (planned)

Training script reads from DB or processed files, writes metrics JSON + model artifact; API serves read-only results.

## Phase 4 — Dashboard (planned)

React calls API; charts show only fields returned by the backend (traceability).
