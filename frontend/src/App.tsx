/**
 * WORKFLOW — operator dashboard; data loads on refresh, not pipeline inspection
 */
import { useCallback, useEffect, useState } from "react";
import {
  fetchDailyDeviations,
  fetchForecastEvaluation,
  fetchForecastMetrics,
  fetchHealthDb,
  fetchQualityEvents,
  fetchTelemetrySummary,
  runPipelineChecklist,
  type PipelineStep,
} from "./api/client";
import { DataSourceBanner } from "./components/DataSourceBanner";
import { DeviationPanel } from "./components/DeviationPanel";
import { ForecastChart } from "./components/ForecastChart";
import { OperatorToolbar } from "./components/OperatorToolbar";
import { PipelineInspect } from "./components/PipelineInspect";
import { QualityEventsPanel } from "./components/QualityEventsPanel";
import { SummaryCards } from "./components/SummaryCards";
import type { DailyDeviationsResponse, ForecastMetrics, QualityEventList, TelemetrySummary } from "./types/api";
import type { EvaluationPoint } from "./types/api";

export default function App() {
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetrySummary | null>(null);
  const [forecast, setForecast] = useState<ForecastMetrics | null>(null);
  const [forecastError, setForecastError] = useState<string | null>(null);
  const [points, setPoints] = useState<EvaluationPoint[]>([]);
  const [quality, setQuality] = useState<QualityEventList | null>(null);
  const [deviations, setDeviations] = useState<DailyDeviationsResponse | null>(null);
  const [deviationError, setDeviationError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(true);
  const [reloadToken, setReloadToken] = useState(0);

  const [inspectSteps, setInspectSteps] = useState<PipelineStep[] | null>(null);
  const [inspectLoading, setInspectLoading] = useState(false);
  const [inspectLastRun, setInspectLastRun] = useState<string | null>(null);

  const refreshData = useCallback(() => setReloadToken((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setRefreshing(true);
      setLoadError(null);
      setForecastError(null);
      setDeviationError(null);

      try {
        await fetchHealthDb();
        if (cancelled) return;
        setApiOk(true);

        const [tel, evalRes, qEvents] = await Promise.all([
          fetchTelemetrySummary(),
          fetchForecastEvaluation(72),
          fetchQualityEvents(),
        ]);
        if (cancelled) return;
        setTelemetry(tel);
        setPoints(evalRes.points);
        setQuality(qEvents);

        try {
          setForecast(await fetchForecastMetrics());
        } catch (e) {
          setForecast(null);
          setForecastError(
            e instanceof Error ? e.message : "Forecast metrics unavailable — run train script."
          );
        }

        try {
          setDeviations(await fetchDailyDeviations());
        } catch (e) {
          setDeviations(null);
          setDeviationError(
            e instanceof Error ? e.message : "Run ml/train_forecast.py for deviation summaries."
          );
        }
      } catch (e) {
        if (!cancelled) {
          setApiOk(false);
          setLoadError(
            e instanceof Error
              ? e.message
              : "Cannot reach API. Start uvicorn on port 8000, then npm run dev."
          );
        }
      } finally {
        if (!cancelled) setRefreshing(false);
      }
    }

    loadDashboard();
    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  async function runInspection() {
    setInspectLoading(true);
    try {
      const steps = await runPipelineChecklist();
      setInspectSteps(steps);
      setInspectLastRun(new Date().toLocaleString());
    } finally {
      setInspectLoading(false);
    }
  }

  const sources = telemetry?.data_sources ?? forecast?.data_sources ?? [];

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Solar Plant Intelligence</h1>
          <p className="subtitle">Plant overview</p>
        </div>
        <span className={`status-dot ${apiOk ? "status-dot--ok" : apiOk === false ? "status-dot--bad" : ""}`}>
          {apiOk ? "Online" : apiOk === false ? "Offline" : "…"}
        </span>
      </header>

      {loadError && <p className="notice notice--error">{loadError}</p>}
      {actionMessage && <p className="notice notice--info">{actionMessage}</p>}
      <DataSourceBanner sources={sources} />

      <OperatorToolbar
        onRefresh={refreshData}
        onActionMessage={setActionMessage}
        refreshing={refreshing}
      />

      <SummaryCards telemetry={telemetry} forecast={forecast} forecastError={forecastError} />

      <div className="cards">
        <QualityEventsPanel data={quality} error={null} />
        <DeviationPanel data={deviations} error={deviationError} />
      </div>

      <ForecastChart points={points} />

      <PipelineInspect
        steps={inspectSteps}
        loading={inspectLoading}
        lastRun={inspectLastRun}
        onRun={runInspection}
      />
    </div>
  );
}
