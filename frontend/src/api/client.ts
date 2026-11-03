/**
 * WORKFLOW — Phase 4 data access + user actions (POST ingest/rescan)
 */
import type {
  DailyDeviationsResponse,
  ForecastEvaluation,
  ForecastMetrics,
  IngestCsvResponse,
  QualityEventList,
  QualityRescanResponse,
  TelemetrySummary,
} from "../types/api";

export type PipelineStep = {
  id: string;
  label: string;
  verifyHint: string;
  status: "pending" | "ok" | "fail" | "warn";
  detail?: string;
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${path} → ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export function fetchTelemetrySummary() {
  return getJson<TelemetrySummary>("/telemetry/summary");
}

export function fetchForecastMetrics() {
  return getJson<ForecastMetrics>("/forecast/metrics");
}

export function fetchForecastEvaluation(limit = 72) {
  return getJson<ForecastEvaluation>(`/forecast/evaluation?limit=${limit}`);
}

export function fetchQualityEvents(limit = 15) {
  return getJson<QualityEventList>(`/telemetry/quality-events?limit=${limit}`);
}

export function fetchDailyDeviations() {
  return getJson<DailyDeviationsResponse>("/forecast/deviations");
}

export function fetchHealthDb() {
  return getJson<{ status: string; database?: string }>("/health/db");
}

export async function uploadCsvFile(file: File): Promise<IngestCsvResponse> {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch("/telemetry/ingest-csv", { method: "POST", body });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail);
  }
  return response.json() as Promise<IngestCsvResponse>;
}

export async function rescanQuality(): Promise<QualityRescanResponse> {
  const response = await fetch("/telemetry/quality/rescan", { method: "POST" });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail);
  }
  return response.json() as Promise<QualityRescanResponse>;
}

export async function runPipelineChecklist(): Promise<PipelineStep[]> {
  const steps: PipelineStep[] = [
    {
      id: "db",
      label: "Database reachable",
      verifyHint: "Engineer: GET /health/db",
      status: "pending",
    },
    {
      id: "telemetry",
      label: "Telemetry stored",
      verifyHint: "Operator: summary card reading count > 0",
      status: "pending",
    },
    {
      id: "quality",
      label: "Quality rules evaluated",
      verifyHint: "Operator: quality events panel",
      status: "pending",
    },
    {
      id: "forecast",
      label: "Forecast artifacts served",
      verifyHint: "Engineer: ml/train_forecast.py then GET /forecast/metrics",
      status: "pending",
    },
    {
      id: "deviation",
      label: "Day deviation narratives",
      verifyHint: "Operator: deviation panel after train",
      status: "pending",
    },
  ];

  try {
    await fetchHealthDb();
    steps[0].status = "ok";
    steps[0].detail = "connected";
  } catch (e) {
    steps[0].status = "fail";
    steps[0].detail = e instanceof Error ? e.message : "failed";
    return steps;
  }

  try {
    const tel = await fetchTelemetrySummary();
    if (tel.reading_count > 0) {
      steps[1].status = "ok";
      steps[1].detail = `${tel.reading_count} readings`;
    } else {
      steps[1].status = "warn";
      steps[1].detail = "Seed demo data or upload CSV";
    }
  } catch (e) {
    steps[1].status = "fail";
    steps[1].detail = e instanceof Error ? e.message : "failed";
  }

  try {
    const q = await fetchQualityEvents(1);
    steps[2].status = "ok";
    steps[2].detail = `${q.count} event(s) listed`;
  } catch (e) {
    steps[2].status = "fail";
    steps[2].detail = e instanceof Error ? e.message : "failed";
  }

  try {
    const m = await fetchForecastMetrics();
    steps[3].status = "ok";
    steps[3].detail = `WAPE ${m.metrics.wape_percent}% (test)`;
  } catch {
    steps[3].status = "warn";
    steps[3].detail = "Run train script locally";
  }

  try {
    const d = await fetchDailyDeviations();
    steps[4].status = d.days.length > 0 ? "ok" : "warn";
    steps[4].detail = `${d.days.length} day summaries`;
  } catch {
    steps[4].status = "warn";
    steps[4].detail = "Needs daily_deviations.json";
  }

  return steps;
}
