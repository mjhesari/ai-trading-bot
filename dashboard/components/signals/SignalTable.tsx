import { Badge } from "@/components/ui/badge";
import { priceDigits } from "@/lib/live-candle";
import type { TradingSignal } from "@/types/signal";

function outcomeBadge(s: TradingSignal) {
  if (s.correct === true) {
    return <Badge variant="success">{s.outcome === "TP2" ? "WIN TP2" : "WIN"}</Badge>;
  }
  if (s.correct === false) {
    return <Badge variant="danger">LOSS</Badge>;
  }
  return <Badge variant="secondary">OPEN</Badge>;
}

export function SignalTable({ signals }: { signals: TradingSignal[] }) {
  if (!signals.length) {
    return <p className="muted">No signals yet — refresh after the engine is up.</p>;
  }

  const ordered = [...signals].reverse();

  return (
    <div className="signal-grid">
      {ordered.map((s, i) => {
        const digits = priceDigits(s.symbol);
        return (
          <article
            key={`${s.time ?? i}-${s.direction}-${s.entry}`}
            className={`signal-card${s.correct === true ? " is-win" : s.correct === false ? " is-loss" : ""}`}
          >
            <div className={`dir-badge ${s.direction === "BUY" ? "buy" : "sell"}`}>{s.direction}</div>
            <div className="signal-meta">
              <div className="title">
                {s.symbol} · {s.timeframe}
                <span className="muted"> · {s.time ? new Date(s.time).toLocaleString() : "—"}</span>
              </div>
              <div className="signal-outcome-row">
                {outcomeBadge(s)}
                {s.rMultiple != null ? (
                  <span className={s.rMultiple >= 0 ? "buy" : "sell"}>
                    {s.rMultiple >= 0 ? "+" : ""}
                    {s.rMultiple.toFixed(2)}R
                  </span>
                ) : (
                  <span className="muted">waiting for SL/TP</span>
                )}
                {s.barsHeld != null ? <span className="muted">{s.barsHeld} bars</span> : null}
              </div>
              <div className="levels">
                <span>Entry {s.entry.toFixed(digits)}</span>
                <span>SL {s.stopLoss.toFixed(digits)}</span>
                <span>TP1 {s.takeProfit1.toFixed(digits)}</span>
                <span>RR {s.riskReward.toFixed(1)}</span>
              </div>
              <div className="reasons">{s.reasons.join(" · ")}</div>
            </div>
            <div className="conf-ring" title="Confidence">
              {Math.round(s.confidence)}
            </div>
          </article>
        );
      })}
    </div>
  );
}
