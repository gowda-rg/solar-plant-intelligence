from pydantic import BaseModel, Field


class ForecastMetricsResponse(BaseModel):
    generated_at: str
    model: str
    target: str
    features: list[str]
    train_rows: int
    test_rows: int
    train_fraction: float
    split_at_measured: str
    data_sources: list[str]
    metrics: dict[str, float]
    notes: list[str] = Field(default_factory=list)


class EvaluationPoint(BaseModel):
    measured_at: str
    actual_kw: float
    predicted_kw: float
    residual_kw: float | None = None


class ForecastEvaluationResponse(BaseModel):
    count: int
    points: list[EvaluationPoint]


class DailyDeviationDay(BaseModel):
    day: str
    actual_kwh: float
    predicted_kwh: float
    deviation_kwh: float
    deviation_pct: float
    mean_abs_residual_kw: float
    summary: str


class DailyDeviationsResponse(BaseModel):
    note: str
    days: list[DailyDeviationDay]
