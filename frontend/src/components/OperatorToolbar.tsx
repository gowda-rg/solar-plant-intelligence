/**
 * WORKFLOW — operator refresh + collapsed engineering lab (rescan / optional CSV)
 */
import { useRef, useState } from "react";
import { rescanQuality, uploadCsvFile } from "../api/client";

type Props = {
  onRefresh: () => void;
  onActionMessage: (msg: string | null) => void;
  refreshing: boolean;
};

export function OperatorToolbar({ onRefresh, onActionMessage, refreshing }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [labOpen, setLabOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  async function runLab(action: () => Promise<void>) {
    setBusy(true);
    onActionMessage(null);
    try {
      await action();
      onRefresh();
    } catch (e) {
      onActionMessage(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel panel--toolbar">
      <div className="panel__head">
        <h2>Overview</h2>
        <button type="button" className="btn" disabled={refreshing || busy} onClick={onRefresh}>
          {refreshing ? "Refreshing…" : "Refresh data"}
        </button>
      </div>
      <details
        className="lab"
        open={labOpen}
        onToggle={(e) => setLabOpen((e.target as HTMLDetailsElement).open)}
      >
        <summary>Engineering lab (ingest & quality)</summary>
        <p className="lab__note">
          Synthetic demo is the default story. CSV ingest adds <code>MEASURED_CSV</code> rows; duplicates
          are skipped. Forecast training stays offline.
        </p>
        <div className="action-row">
          <button
            type="button"
            className="btn btn--secondary"
            disabled={busy}
            onClick={() =>
              runLab(async () => {
                const result = await rescanQuality();
                onActionMessage(result.message);
              })
            }
          >
            Re-scan quality
          </button>
          <button
            type="button"
            className="btn btn--secondary"
            disabled={busy}
            onClick={() => fileRef.current?.click()}
          >
            Upload CSV
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".csv,text/csv"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              void runLab(async () => {
                const result = await uploadCsvFile(file);
                onActionMessage(result.message);
              });
              e.target.value = "";
            }}
          />
        </div>
      </details>
    </section>
  );
}
