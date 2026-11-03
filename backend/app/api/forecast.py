# =============================================================================
# WORKFLOW — Phase 3d: expose offline training results over HTTP
# =============================================================================
# Does NOT train models on request — only reads JSON artifacts from ml/artifacts/
# RUN train first: cd backend && PYTHONPATH=. python3 ../ml/train_forecast.py
# CHECK: GET /forecast/metrics, /forecast/evaluation, /forecast/deviations
# MAP:   ml/train_forecast.py header
# =============================================================================
from fastapi import APIRouter, HTTPException, Query

from app.schemas.forecast import (
    DailyDeviationsResponse,
    ForecastEvaluationResponse,
    ForecastMetricsResponse,
)
from app.services import forecast_artifacts

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/metrics", response_model=ForecastMetricsResponse)
def forecast_metrics() -> ForecastMetricsResponse:
    try:
        data = forecast_artifacts.load_metrics()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ForecastMetricsResponse(**data)


@router.get("/evaluation", response_model=ForecastEvaluationResponse)
def forecast_evaluation(
    limit: int = Query(default=48, ge=1, le=500),
) -> ForecastEvaluationResponse:
    try:
        data = forecast_artifacts.load_evaluation_points(limit=limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ForecastEvaluationResponse(**data)


@router.get("/deviations", response_model=DailyDeviationsResponse)
def forecast_deviations() -> DailyDeviationsResponse:
    try:
        data = forecast_artifacts.load_daily_deviations()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DailyDeviationsResponse(**data)
