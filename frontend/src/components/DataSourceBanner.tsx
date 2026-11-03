/**
 * WORKFLOW — honesty layer for operators and reviewers
 * Shows when telemetry is synthetic so the UI never implies live SCADA without a label.
 */
type Props = {
  sources: string[];
};

export function DataSourceBanner({ sources }: Props) {
  const synthetic = sources.some((s) => s.includes("SYNTHETIC"));
  if (!synthetic) {
    return null;
  }

  return (
    <div className="banner banner--demo" role="status">
      Data sources: {sources.join(", ")} (demo / measured export — not live SCADA).
    </div>
  );
}
