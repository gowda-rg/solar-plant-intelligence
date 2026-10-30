# Data directory

## Provenance policy

All files under `raw/` and `processed/` must document:

1. **Source** (URL, publisher, license)  
2. **Type:** `MEASURED` (public real data) or `SYNTHETIC` (generated for demo)  
3. **Time range and granularity**  
4. **Columns and units**  

Nothing in the application UI may present synthetic data as live plant SCADA without an explicit label.

## Planned content

- `raw/` — downloaded CSV or similar (to be added after dataset approval)  
- `processed/` — cleaned tables ready for load or feature engineering  

## Dataset candidates (for approval)

Public PV or plant output time series combined with irradiance or weather features—selected for chronological forecasting exercises, not for claiming affiliation with a specific utility-scale site.
