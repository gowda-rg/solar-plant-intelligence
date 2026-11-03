# Solar Plant Intelligence

End-to-end demonstration of **solar telemetry analytics**, **day-ahead generation forecasting**, **data quality monitoring**, and **operator-oriented dashboards**—patterns used in utility-scale solar monitoring platforms.

## Problem statement

Operators and analysts need trustworthy views of plant output, forecast performance, and unusual deviations—not charts backed by unverified or mislabeled data. This project implements an **MVP** that ingests time-series plant and weather-related signals, validates data quality, trains and evaluates a forecasting model with **time-aware validation**, surfaces residuals and anomalies, and exposes results through a **FastAPI** backend and **React** frontend backed by **PostgreSQL**.

This is a **development and learning MVP**, not a production SCADA or historian replacement.

## Capabilities (MVP scope)

- Telemetry ingestion and structured storage  
- Data validation and quality flags (gaps, duplicates, stale readings)  
- Day-ahead (or horizon-appropriate) power forecasting with **chronological train/test splits**  
- Reported metrics: **MAE**, **RMSE**, **WAPE** (computed from held-out evaluation, not hand-entered)  
- Forecast deviation / residual analysis with day-level summaries (`daily_deviations.json`, `/forecast/deviations`)  
- Ingest-time quality flags (gaps, stale/flat output, duplicates) with `/telemetry/quality-events`  
- REST API for measurements, forecasts, and quality summaries  
- React dashboard with trend and forecast-vs-actual views (Recharts)  

Out of scope for v1: OPC UA/Modbus live SCADA, LLM assistants, automated PDF/email reporting, string-level analytics at full plant scale.

## Tech stack

| Layer | Technology |
|-------|------------|
| API | Python 3.10+, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| ML | pandas, NumPy, scikit-learn |
| UI | React, Recharts |
| Tooling | Git, pytest (API and metric sanity checks) |

## Repository layout

```
backend/     FastAPI application and persistence
frontend/    React operator dashboard
ml/          Training, evaluation artifacts, anomaly logic
data/        Raw and processed datasets (with provenance README)
scripts/     Ingest and database seed utilities
docs/        Architecture and engineering decisions
```

## Data integrity

- Every dataset is labeled **measured (public source)** or **synthetic (demo)** in `data/README.md`.  
- Model metrics displayed in the UI originate from evaluation scripts stored in the repository.  
- Time-series models use **chronological splitting**; random shuffles are not used for forecast validation.  

## Local development

Prerequisites: Python 3.10+, Node.js 18+, PostgreSQL, Git.

### Backend (current)

```bash
cd backend
python3 -m pip install -r requirements.txt
PYTHONPATH=. python3 -m pytest tests/test_health.py -q
PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- `GET /health` — process up  
- `GET /health/db` — PostgreSQL reachable via `DATABASE_URL` in `backend/.env`  
- `GET /telemetry/summary` — row counts and data source labels (after seed)

### Database + demo telemetry (Phase 2)

```bash
cd backend
PYTHONPATH=. python3 scripts/init_db.py
PYTHONPATH=. python3 scripts/seed_demo_data.py
```

### Forecast training (Phase 3)

```bash
cd backend
PYTHONPATH=. python3 ../ml/train_forecast.py
# Then: GET /forecast/metrics and /forecast/evaluation on the running API
PYTHONPATH=. python3 -m pytest tests/ -q
```

### Frontend dashboard (Phase 4)

```bash
# Terminal 1 — API
cd backend && PYTHONPATH=. uvicorn app.main:app --reload --port 8000

# Terminal 2 — UI (proxies API in dev)
cd frontend && npm install && npm run dev
```

Open http://127.0.0.1:5173 — workflow map in `frontend/src/App.tsx`. Step-by-step practice: `docs/DEMO_FLOW.md`.


## License

TBD.

## Author

gowda-rg
