/**
 * WORKFLOW — Phase 3 forecast deviation (held-out test days)
 * Source: GET /forecast/deviations — daily energy vs forecast with plain-language summary
 */
import type { DailyDeviationsResponse } from "../types/api";

type Props = {
  data: DailyDeviationsResponse | null;
  error: string | null;
};

export function DeviationPanel({ data, error }: Props) {
  return (
    <section className="card">
      <h2>Day-level forecast deviation</h2>
      {error && <p className="error">{error}</p>}
      {!data && !error && <p className="muted">Loading…</p>}
      {data && (
        <>
          <p className="footnote">{data.note}</p>
          <ul className="deviation-list">
            {data.days.map((day) => (
              <li key={day.day}>
                <div className="deviation-list__head">
                  <strong>{day.day}</strong>
                  <span>
                    Δ {day.deviation_kwh} kWh ({day.deviation_pct}%)
                  </span>
                </div>
                <p className="deviation-list__summary">{day.summary}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
