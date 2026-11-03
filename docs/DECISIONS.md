# Engineering decisions log

Concise record of technical choices and rationale.

| Date | Decision | Rationale | Alternatives considered |
|------|----------|-----------|-------------------------|
| 2026-10-30 | Monorepo with `backend/`, `frontend/`, `ml/` | Clear boundaries for API, UI, and offline training | Separate repositories (heavier for MVP) |
| 2026-10-30 | PostgreSQL | Time-series aggregations, indexing, and relational integrity | SQLite (simpler but limited concurrency story) |
| 2026-10-30 | scikit-learn baseline forecaster | Fast chronological validation; interpretable features | Deep learning (overkill for MVP timeline) |
| 2026-10-31 | Demo data `SYNTHETIC_DEMO` via seed script | Unblocks ingest/API/ML without external downloads; clearly labeled | Public CSV only (deferred) |
| 2026-10-31 | Learning notes in source as `SEMANTIC` comments | Inspect code while stepping through the system | Separate doc-only dev journals |

| 2026-11-03 | GradientBoostingRegressor + lag/irradiance features | Nonlinear baseline; chronological 80/20 split | Ridge (linear only) |
| 2026-11-03 | Metrics in `ml/artifacts/metrics.json` | API reads file; numbers trace to train script | Recompute metrics in API (would hide methodology) |

## Pending

- Dataset selection and citation URL  
- Exact forecast horizon (day-ahead vs rolling 24h)  
- Anomaly method (residual threshold vs isolation forest on features)  
