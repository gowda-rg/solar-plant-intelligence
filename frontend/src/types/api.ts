/** Shapes mirror backend Pydantic schemas — keep in sync when API changes. */

export type TelemetrySummary = {
  reading_count: number;
  quality_event_count: number;
  first_reading_at: string | null;
  last_reading_at: string | null;
  data_sources: string[];
};

export type ForecastMetrics = {
  generated_at: string;
  model: string;
  target: string;
  features: string[];
  train_rows: number;
  test_rows: number;
  train_fraction: number;
  split_at_measured: string;
  data_sources: string[];
  metrics: {
    mae_kw: number;
    rmse_kw: number;
    wape_percent: number;
  };
  notes: string[];
};

export type EvaluationPoint = {
  measured_at: string;
  actual_kw: number;
  predicted_kw: number;
  residual_kw?: number;
};

export type ForecastEvaluation = {
  count: number;
  points: EvaluationPoint[];
};

export type QualityEvent = {
  id: number;
  detected_at: string;
  rule_code: string;
  severity: string;
  message: string;
};

export type QualityEventList = {
  count: number;
  events: QualityEvent[];
};

export type DailyDeviationDay = {
  day: string;
  actual_kwh: number;
  predicted_kwh: number;
  deviation_kwh: number;
  deviation_pct: number;
  mean_abs_residual_kw: number;
  summary: string;
};

export type DailyDeviationsResponse = {
  note: string;
  days: DailyDeviationDay[];
};

export type IngestCsvResponse = {
  rows_inserted: number;
  rows_skipped_duplicates: number;
  quality_events_created: number;
  data_source: string;
  message: string;
};

export type QualityRescanResponse = {
  quality_events_stored: number;
  message: string;
};
