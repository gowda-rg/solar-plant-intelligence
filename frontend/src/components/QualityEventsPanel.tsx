/**
 * WORKFLOW — Phase 2 quality visibility
 * Source: GET /telemetry/quality-events (PostgreSQL quality_events table)
 */
import type { QualityEventList } from "../types/api";

type Props = {
  data: QualityEventList | null;
  error: string | null;
};

export function QualityEventsPanel({ data, error }: Props) {
  return (
    <section className="card">
      <h2>Data quality events</h2>
      {error && <p className="error">{error}</p>}
      {!data && !error && <p className="muted">Loading…</p>}
      {data && data.count === 0 && (
        <p className="muted">No events stored. Reseed or run rescan_quality.py.</p>
      )}
      {data && data.events.length > 0 && (
        <ul className="event-list">
          {data.events.map((ev) => (
            <li key={ev.id}>
              <span className={`tag tag--${ev.severity}`}>{ev.rule_code}</span>
              <p>{ev.message}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
