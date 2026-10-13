import type { BacktestMetrics } from "@/types/backtest";

export function MetricsPanel({ metrics }: { metrics: BacktestMetrics }) {
  const items: Array<[string, string]> = [
    ["Trades", String(metrics.totalTrades)],
    ["Wins / Losses", `${metrics.wins ?? "—"} / ${metrics.losses ?? "—"}`],
    ["Win Rate", `${metrics.winRate}%`],
    ["Profit Factor", String(metrics.profitFactor)],
    ["Expectancy", String(metrics.expectancy)],
    ["Max DD", `${metrics.maxDrawdown}%`],
    ["Avg R", String(metrics.averageR)],
    ["Avg lot", String(metrics.avgLots ?? "—")],
    ["Sharpe", String(metrics.sharpe)],
    ["Return", `${metrics.returnPct}%`],
    ["Start", String(metrics.initialBalance ?? "—")],
    ["Final Balance", String(metrics.finalBalance)],
  ];

  return (
    <div className="metrics">
      {items.map(([label, value]) => (
        <div key={label} className="metric">
          <span className="label">{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}
