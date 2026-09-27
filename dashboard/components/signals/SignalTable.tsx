import type { TradingSignal } from "@/types/signal";

export function SignalTable({ signals }: { signals: TradingSignal[] }) {
  if (!signals.length) {
    return <p className="muted">No signals yet — refresh after the engine is up.</p>;
  }

  const ordered = [...signals].reverse();

  return (
    <div className="signal-grid">
      {ordered.map((s, i) => (
        <article key={`${s.time ?? i}-${s.direction}-${s.entry}`} className="signal-card">
          <div className={`dir-badge ${s.direction === "BUY" ? "buy" : "sell"}`}>{s.direction}</div>
          <div className="signal-meta">
            <div className="title">
              {s.symbol} · {s.timeframe}
              <span className="muted"> · {s.time ? new Date(s.time).toLocaleString() : "—"}</span>
            </div>
            <div className="levels">
              <span>Entry {s.entry.toFixed(5)}</span>
              <span>SL {s.stopLoss.toFixed(5)}</span>
              <span>TP1 {s.takeProfit1.toFixed(5)}</span>
              <span>RR {s.riskReward.toFixed(1)}</span>
            </div>
            <div className="reasons">{s.reasons.join(" · ")}</div>
          </div>
          <div className="conf-ring" title="Confidence">
            {Math.round(s.confidence)}
          </div>
        </article>
      ))}
    </div>
  );
}
