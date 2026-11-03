/**
 * WORKFLOW — Phase 4 visualization
 * IN:  points from GET /forecast/evaluation (held-out test period only)
 * OUT: Recharts lines — actual vs predicted power (kW)
 * SAY:  "Chart points are API JSON, same data produced by ml/train_forecast.py on the test split."
 */
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EvaluationPoint } from "../types/api";

type Props = {
  points: EvaluationPoint[];
};

export function ForecastChart({ points }: Props) {
  const data = points.map((p) => ({
    time: new Date(p.measured_at).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
    }),
    actual: p.actual_kw,
    predicted: p.predicted_kw,
  }));

  return (
    <section className="card card--chart">
      <h2>Actual vs predicted (held-out test)</h2>
      {points.length === 0 ? (
        <p className="muted">No evaluation points. Run ml/train_forecast.py and refresh.</p>
      ) : (
        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis unit=" kW" tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual kW"
              stroke="#38bdf8"
              dot={false}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              name="Predicted kW"
              stroke="#fbbf24"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}
