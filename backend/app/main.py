from fastapi import FastAPI, HTTPException

from app.database import check_database_connection

app = FastAPI(
    title="Solar Plant Intelligence API",
    description="Telemetry, forecasting, and data quality services for solar plant analytics.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        check_database_connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok", "database": "connected"}
