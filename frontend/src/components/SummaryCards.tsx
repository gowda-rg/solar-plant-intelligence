/**
 * WORKFLOW — Phase 4 summary row
 * Left card: Phase 2 persistence (/telemetry/summary)
 * Right card: Phase 3 offline model metrics (/forecast/metrics) — not recomputed in the browser
 */
import type { ForecastMetrics, TelemetrySummary } from "../types/api";

type Props = {
  telemetry: TelemetrySummary | null;
  forecast: ForecastMetrics | null;
  forecastError: string | null;
};

function formatRange(start: string | null, end: string | null): string {
  if (!start || !end) return "—";
  const s = new Date(start).toLocaleString();
  const e = new Date(end).toLocaleString();
  return `${s} → ${e}`;
}

export function SummaryCards({ telemetry, forecast, forecastError }: Props) {
  return (
    <div className="cards">
      <section className="card">
        <h2>Telemetry</h2>
        {telemetry ? (
          <ul className="stat-list">
            <li>
              <span>Readings</span>
              <strong>{telemetry.reading_count}</strong>
            </li>
            <li>
              <span>Quality events</span>
              <strong>{telemetry.quality_event_count}</strong>
            </li>
            <li>
              <span>Time range</span>
              <strong className="stat-list__wide">
                {formatRange(telemetry.first_reading_at, telemetry.last_reading_at)}
              </strong>
            </li>
          </ul>
        ) : (
          <p className="muted">Loading…</p>
        )}
      </section>

      <section className="card">
        <h2>Forecast evaluation</h2>
        {forecastError && <p className="error">{forecastError}</p>}
        {forecast ? (
          <>
            <ul className="stat-list">
              <li>
                <span>MAE (test)</span>
                <strong>{forecast.metrics.mae_kw} kW</strong>
              </li>
              <li>
                <span>RMSE (test)</span>
                <strong>{forecast.metrics.rmse_kw} kW</strong>
              </li>
              <li>
                <span>WAPE (test)</span>
                <strong>{forecast.metrics.wape_percent}%</strong>
              </li>
              <li>
                <span>Chronological split at</span>
                <strong className="stat-list__wide">
                  {new Date(forecast.split_at_measured).toLocaleString()}
                </strong>
              </li>
              <li>
                <span>Model</span>
                <strong>{forecast.model}</strong>
              </li>
            </ul>
            <p className="footnote">{forecast.notes[0]}</p>
          </>
        ) : (
          !forecastError && <p className="muted">Loading…</p>
        )}
      </section>
    </div>
  );
}
