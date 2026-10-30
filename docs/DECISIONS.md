# Engineering decisions log

Concise record of technical choices and rationale.

| Date | Decision | Rationale | Alternatives considered |
|------|----------|-----------|-------------------------|
| 2026-10-30 | Monorepo with `backend/`, `frontend/`, `ml/` | Clear boundaries for API, UI, and offline training | Separate repositories (heavier for MVP) |
| 2026-10-30 | PostgreSQL | Time-series aggregations, indexing, and relational integrity | SQLite (simpler but limited concurrency story) |
| 2026-10-30 | scikit-learn baseline forecaster | Fast chronological validation; interpretable features | Deep learning (overkill for MVP timeline) |
| 2026-10-30 | Private notes outside git root | Public repo contains only product/engineering artifacts | Single folder mixing public and private docs |

## Pending

- Dataset selection and citation URL  
- Exact forecast horizon (day-ahead vs rolling 24h)  
- Anomaly method (residual threshold vs isolation forest on features)  
