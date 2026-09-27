import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="page">
      <h1>Dashboard</h1>
      <p className="muted">Monitor signals and run rule-based SMC backtests.</p>
      <div className="panel">
        <ul>
          <li>
            <Link href="/dashboard/signals">Signals</Link> — latest BUY/SELL setups
          </li>
          <li>
            <Link href="/dashboard/backtest">Backtest</Link> — run SMC V1 on sample data
          </li>
          <li>
            <Link href="/dashboard/charts">Charts</Link> — placeholder
          </li>
          <li>
            <Link href="/dashboard/settings">Settings</Link> — placeholder
          </li>
        </ul>
      </div>
    </main>
  );
}
