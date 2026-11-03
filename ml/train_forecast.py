#!/usr/bin/env python3
# =============================================================================
# PROJECT WORKFLOW MAP — Phase 3: offline forecast training (chronological)
# =============================================================================
# Prerequisites: Phase 2 complete (plant_readings populated — run seed_demo_data.py)
#
# INPUT:  Rows from PostgreSQL plant_readings (measured_at, power_kw, irradiance_wm2)
# OUTPUT: ml/artifacts/metrics.json       — MAE, RMSE, WAPE on held-out tail
#         ml/artifacts/evaluation_points.json — actual vs predicted for charts/API
#         ml/artifacts/model.joblib       — fitted pipeline (gitignored; regenerate locally)
#
# RUN (from repository root):
#   pip install -r backend/requirements.txt   # once, includes sklearn/pandas
#   cd backend && PYTHONPATH=. python3 ../ml/train_forecast.py
#
# CHECK:
#   cat ml/artifacts/metrics.json
#   curl http://127.0.0.1:8000/forecast/metrics   (after uvicorn + train)
#   curl http://127.0.0.1:8000/forecast/evaluation?limit=24
#
# VALIDATION RULE:
#   Train/test split is by TIME (first 80% train, last 20% test) — never shuffle rows.
#   Scaler and model fit on train only; metrics computed on test only.
#
# Phase 4 next: frontend charts read /forecast/evaluation (no hand-entered metrics).
# Full phase list: backend/scripts/seed_demo_data.py header
# =============================================================================
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
ARTIFACTS_DIR = REPO_ROOT / "ml" / "artifacts"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.database import get_engine  # noqa: E402
from app.models import PlantReading  # noqa: E402

FEATURE_COLUMNS = [
    "hour_sin",
    "hour_cos",
    "irradiance_wm2",
    "power_kw_lag_1",
    "power_kw_lag_24",
]
TARGET_COLUMN = "power_kw"
TRAIN_FRACTION = 0.8
EVAL_POINTS_LIMIT = 168  # one week hourly for API default payload size


def wape(actual: np.ndarray, predicted: np.ndarray) -> float:
    denom = np.sum(np.abs(actual))
    if denom == 0:
        return float("nan")
    return float(np.sum(np.abs(actual - predicted)) / denom * 100.0)


def load_readings_frame() -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                PlantReading.measured_at,
                PlantReading.power_kw,
                PlantReading.irradiance_wm2,
                PlantReading.data_source,
            ).order_by(PlantReading.measured_at)
        ).all()

    if not rows:
        raise SystemExit("No plant_readings found. Run Phase 2 seed_demo_data.py first.")

    df = pd.DataFrame(rows, columns=["measured_at", "power_kw", "irradiance_wm2", "data_source"])
    df["measured_at"] = pd.to_datetime(df["measured_at"], utc=True)
    return df


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values("measured_at").copy()
    hour = out["measured_at"].dt.hour + out["measured_at"].dt.minute / 60.0
    out["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
    out["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
    out["irradiance_wm2"] = out["irradiance_wm2"].fillna(0.0)
    out["power_kw_lag_1"] = out["power_kw"].shift(1)
    out["power_kw_lag_24"] = out["power_kw"].shift(24)
    out = out.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])
    return out


def chronological_split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(frame) * TRAIN_FRACTION)
    if split_idx < 10 or len(frame) - split_idx < 5:
        raise SystemExit(f"Not enough rows after feature build ({len(frame)}). Need more telemetry.")
    train = frame.iloc[:split_idx]
    test = frame.iloc[split_idx:]
    return train, test


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[("features", StandardScaler(), FEATURE_COLUMNS)],
        remainder="drop",
    )
    model = GradientBoostingRegressor(
        random_state=42,
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def main() -> None:
    raw = load_readings_frame()
    featured = build_feature_frame(raw)
    train_df, test_df = chronological_split(featured)

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    mae = float(mean_absolute_error(y_test, predictions))
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    wape_pct = wape(y_test.to_numpy(), predictions)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACTS_DIR / "model.joblib"
    joblib.dump(pipeline, model_path)

    split_at = test_df["measured_at"].iloc[0]
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "GradientBoostingRegressor",
        "target": TARGET_COLUMN,
        "features": FEATURE_COLUMNS,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_fraction": TRAIN_FRACTION,
        "split_at_measured": split_at.isoformat(),
        "data_sources": sorted(raw["data_source"].unique().tolist()),
        "metrics": {
            "mae_kw": round(mae, 4),
            "rmse_kw": round(rmse, 4),
            "wape_percent": round(wape_pct, 4),
        },
        "notes": [
            "Chronological train/test split; no random shuffle.",
            "Metrics computed on held-out test period only.",
            "Synthetic demo data — not industrial forecast accuracy.",
        ],
    }
    metrics_path = ARTIFACTS_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    eval_rows = []
    residuals = y_test.to_numpy() - predictions
    for ts, actual, pred, residual in zip(
        test_df["measured_at"].iloc[:EVAL_POINTS_LIMIT],
        y_test.iloc[:EVAL_POINTS_LIMIT],
        predictions[:EVAL_POINTS_LIMIT],
        residuals[:EVAL_POINTS_LIMIT],
    ):
        eval_rows.append(
            {
                "measured_at": ts.isoformat(),
                "actual_kw": round(float(actual), 4),
                "predicted_kw": round(float(pred), 4),
                "residual_kw": round(float(residual), 4),
            }
        )
    eval_path = ARTIFACTS_DIR / "evaluation_points.json"
    eval_path.write_text(json.dumps({"points": eval_rows}, indent=2), encoding="utf-8")

    test_eval = test_df.copy()
    test_eval["predicted_kw"] = predictions
    test_eval["residual_kw"] = test_eval[TARGET_COLUMN] - test_eval["predicted_kw"]
    test_eval["day"] = test_eval["measured_at"].dt.date.astype(str)
    daily = (
        test_eval.groupby("day")
        .agg(
            actual_kwh=("power_kw", "sum"),
            predicted_kwh=("predicted_kw", "sum"),
            mean_abs_residual=("residual_kw", lambda s: float(np.mean(np.abs(s)))),
        )
        .reset_index()
    )
    daily["deviation_kwh"] = daily["actual_kwh"] - daily["predicted_kwh"]
    daily["deviation_pct"] = np.where(
        daily["predicted_kwh"] > 0,
        (daily["deviation_kwh"] / daily["predicted_kwh"]) * 100.0,
        0.0,
    )

    deviation_rows = []
    ranked = daily.assign(abs_dev=daily["deviation_kwh"].abs()).sort_values(
        "abs_dev", ascending=False
    )
    for _, row in ranked.head(5).iterrows():
        shortfall = float(row["deviation_kwh"]) < 0
        direction = "below" if shortfall else "above"
        deviation_rows.append(
            {
                "day": row["day"],
                "actual_kwh": round(float(row["actual_kwh"]), 3),
                "predicted_kwh": round(float(row["predicted_kwh"]), 3),
                "deviation_kwh": round(float(row["deviation_kwh"]), 3),
                "deviation_pct": round(float(row["deviation_pct"]), 2),
                "mean_abs_residual_kw": round(float(row["mean_abs_residual"]), 4),
                "summary": (
                    f"Actual energy was {abs(row['deviation_pct']):.1f}% {direction} forecast "
                    f"({row['deviation_kwh']:.2f} kWh delta). Review weather, curtailment, or "
                    f"data quality on this day — not a confirmed equipment fault."
                ),
            }
        )

    deviations_path = ARTIFACTS_DIR / "daily_deviations.json"
    deviations_path.write_text(
        json.dumps(
            {
                "note": "Daily sums on held-out test period only.",
                "days": deviation_rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {metrics_path}")
    print(f"Wrote {eval_path}")
    print(f"Wrote {deviations_path}")
    print(f"Wrote {model_path} (local only; gitignored)")
    print(
        f"Test MAE={metrics['metrics']['mae_kw']} kW, "
        f"RMSE={metrics['metrics']['rmse_kw']} kW, "
        f"WAPE={metrics['metrics']['wape_percent']}%"
    )
    print(f"Database URL host used: {settings.database_url.split('@')[-1]}")


if __name__ == "__main__":
    main()
