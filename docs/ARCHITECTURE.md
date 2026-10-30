# Architecture — Solar Plant Intelligence MVP

## Goals

1. **Traceability:** UI numbers map to database rows or documented model outputs.  
2. **Time-series correctness:** No leakage across train/test; preprocessing fit on training data only.  
3. **Maintainability:** Small team–sized codebase with clear module boundaries and documented data flow.  
4. **Delivery:** Working vertical slice before optional enhancements.

## Logical architecture

```
┌─────────────┐     HTTP      ┌──────────────┐     SQL      ┌────────────┐
│   React UI  │ ◄──────────► │   FastAPI    │ ◄──────────► │ PostgreSQL │
└─────────────┘               └──────┬───────┘              └────────────┘
                                     │
                              reads metrics &
                              model metadata
                                     ▼
                              ┌──────────────┐
                              │  ml/ scripts │
                              │  (offline)   │
                              └──────────────┘
```

## Data pipeline

| Stage | Input | Processing | Output | Verification |
|-------|--------|------------|--------|--------------|
| Ingest | CSV or API-export files | Parse timestamps, normalize units, reject invalid rows | Rows in `telemetry` tables | Row counts, null checks, duplicate timestamp detection |
| Quality | Stored telemetry | Rules for gaps, flatlines, out-of-range | `quality_events` or flag columns | Unit tests on known bad samples |
| Features | Telemetry + weather | Lags, rolling stats, calendar features | Feature matrix `X`, target `y` | No future data in features for each prediction time |
| Train/eval | Feature matrix | Chronological split; fit scaler/model on train only | Model artifact + JSON metrics | Compare metrics script vs API payload |
| Infer | Latest features | Load persisted model | Forecast rows | Spot-check against offline script |
| Anomalies | Forecast residuals | Threshold or robust z-score on residuals | Anomaly records | Manual review on sample days |

## Backend modules (planned)

- `app/main.py` — application factory, CORS for local frontend  
- `app/api/` — routes: health, telemetry, forecasts, quality, anomalies  
- `app/models/` — SQLAlchemy ORM models  
- `app/services/` — query and aggregation logic  
- `app/schemas/` — Pydantic request/response models  
- `tests/` — API contracts and metric calculation tests  

## Frontend views (planned)

1. **Overview** — recent power, daily energy, active quality flags  
2. **Forecast** — day-ahead curve vs actual, error metrics from backend  
3. **Quality** — timeline of validation events  
4. **Anomalies** — ranked residual-based alerts with disclaimer (not confirmed equipment faults)  

## Deployment assumption

Local development only for MVP: single PostgreSQL instance, backend on `localhost:8000`, frontend dev server with proxy to API.

## Security note

No authentication in MVP (local demo). Production would add operator auth, audit logging, and network isolation for plant networks.
