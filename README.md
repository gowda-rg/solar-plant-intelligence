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
- Forecast deviation / residual analysis and simple anomaly scoring  
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

### Database setup

```bash
cd backend
PYTHONPATH=. python scripts/init_db.py
PYTHONPATH=. python scripts/seed_demo_data.py   # optional SYNTHETIC_DEMO rows
```

Read `SEMANTIC` comment blocks at the top of modules under `backend/app/` when tracing the flow.

## License

TBD.

## Author

gowda-rg
