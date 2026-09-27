import type { TradingSignal } from "@/types/signal";

export function SignalTable({ signals }: { signals: TradingSignal[] }) {
  if (!signals.length) {
    return <p className="muted">No signals yet.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Dir</th>
            <th>Entry</th>
            <th>SL</th>
            <th>TP1</th>
            <th>RR</th>
            <th>Conf</th>
            <th>Reasons</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((s, i) => (
            <tr key={`${s.time ?? i}-${s.direction}`}>
              <td>{s.time ? new Date(s.time).toLocaleString() : "—"}</td>
              <td className={s.direction === "BUY" ? "buy" : "sell"}>{s.direction}</td>
              <td>{s.entry.toFixed(5)}</td>
              <td>{s.stopLoss.toFixed(5)}</td>
              <td>{s.takeProfit1.toFixed(5)}</td>
              <td>{s.riskReward.toFixed(1)}</td>
              <td>{Math.round(s.confidence)}</td>
              <td className="reasons">{s.reasons.join(" · ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
