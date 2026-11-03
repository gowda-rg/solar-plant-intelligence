# =============================================================================
# WORKFLOW — Phase 3d: read ml/artifacts/*.json from the API layer
# =============================================================================
# Written by: ml/train_forecast.py (offline, not inside uvicorn)
# Read by:    app/api/forecast.py
# CHECK:      files exist after running train script from repo root instructions
# =============================================================================
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "ml" / "artifacts"


def artifacts_dir() -> Path:
    return ARTIFACTS_DIR


def load_metrics() -> dict:
    path = ARTIFACTS_DIR / "metrics.json"
    if not path.is_file():
        raise FileNotFoundError(
            "metrics.json missing. Run: cd backend && PYTHONPATH=. python3 ../ml/train_forecast.py"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_evaluation_points(limit: int | None = None) -> dict:
    path = ARTIFACTS_DIR / "evaluation_points.json"
    if not path.is_file():
        raise FileNotFoundError(
            "evaluation_points.json missing. Run the Phase 3 train script first."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    points = payload.get("points", [])
    if limit is not None and limit > 0:
        points = points[:limit]
    return {"points": points, "count": len(points)}


def load_daily_deviations() -> dict:
    path = ARTIFACTS_DIR / "daily_deviations.json"
    if not path.is_file():
        raise FileNotFoundError(
            "daily_deviations.json missing. Re-run ml/train_forecast.py after updating train script."
        )
    return json.loads(path.read_text(encoding="utf-8"))
