/**
 * WORKFLOW — engineer smoke test; runs only when user clicks "Run inspection"
 */
import type { PipelineStep } from "../api/client";

type Props = {
  steps: PipelineStep[] | null;
  loading: boolean;
  lastRun: string | null;
  onRun: () => void;
};

function statusLabel(status: PipelineStep["status"]): string {
  if (status === "ok") return "PASS";
  if (status === "fail") return "FAIL";
  if (status === "warn") return "WARN";
  return "—";
}

export function PipelineInspect({ steps, loading, lastRun, onRun }: Props) {
  return (
    <section className="panel panel--inspect">
      <div className="panel__head">
        <div>
          <h2>Pipeline inspection</h2>
          <p className="panel__desc">Optional API smoke checks (same idea as DevTools / curl).</p>
        </div>
        <button type="button" className="btn btn--secondary" disabled={loading} onClick={onRun}>
          {loading ? "Running…" : "Run inspection"}
        </button>
      </div>
      {lastRun && <p className="panel__meta">Last run: {lastRun}</p>}
      {steps && steps.length > 0 && (
        <table className="inspect-table">
          <thead>
            <tr>
              <th>Check</th>
              <th>Status</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {steps.map((step) => (
              <tr key={step.id}>
                <td>
                  <div className="inspect-table__label">{step.label}</div>
                  <div className="inspect-table__hint">{step.verifyHint}</div>
                </td>
                <td>
                  <span className={`badge badge--${step.status}`}>{statusLabel(step.status)}</span>
                </td>
                <td className="inspect-table__detail">{step.detail ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
