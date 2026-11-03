# Data directory

## Provenance policy

All files under `raw/` and `processed/` must document:

1. **Source** (URL, publisher, license)  
2. **Type:** `MEASURED` (public real data) or `SYNTHETIC` (generated for demo)  
3. **Time range and granularity**  
4. **Columns and units**  

Nothing in the application UI may present synthetic data as live plant SCADA without an explicit label.

## Current MVP data

| Label            | Type            | Origin                                                                                                                   |
| ---------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `SYNTHETIC_DEMO` | SYNTHETIC       | `backend/scripts/seed_demo_data.py` (includes intentional gap + flatline for quality demos)                              |
| `MEASURED_CSV`   | MEASURED (file) | `backend/scripts/ingest_csv.py` — e.g. `data/raw/example_plant_export.csv` (sample rows; replace with cited public data) |

## CSV format for ingest

```csv
measured_at,power_kw,irradiance_wm2
2026-10-01T10:00:00+00:00,3.42,720
```

Run: `cd backend && PYTHONPATH=. python3 scripts/ingest_csv.py ../data/raw/example_plant_export.csv`

## Planned content

- `raw/` — downloaded CSV or similar  
- `processed/` — cleaned exports aligned with ingest scripts  
