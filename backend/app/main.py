# =============================================================================
# WORKFLOW — Phase 1 + route registration
# =============================================================================
# Phase 1 endpoints: /health (process only), /health/db (PostgreSQL via database.py)
# Phase 2 routes:    telemetry_router → GET /telemetry/summary
# Phase 3 routes:    forecast_router → GET /forecast/metrics, /forecast/evaluation
#
# Phase 4 — frontend dev server (Vite :5173) uses vite proxy; CORS helps preview/build modes
#
# CHECK:  /docs for all routes; exercise each tab after running init_db + seed scripts
# MAP:    Full phase list in scripts/seed_demo_data.py header
# =============================================================================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.forecast import router as forecast_router
from app.api.telemetry import router as telemetry_router
from app.database import check_database_connection

app = FastAPI(
    title="Solar Plant Intelligence API",
    description="Telemetry, forecasting, and data quality services for solar plant analytics.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(telemetry_router)
app.include_router(forecast_router)


@app.get("/health")
def health():
    # Phase 1 — does not use the database
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    # Phase 1 — same connection path as pytest test_health_db
    try:
        check_database_connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok", "database": "connected"}
