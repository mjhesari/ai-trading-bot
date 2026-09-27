import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page hero">
      <h1>AI Trading Bot</h1>
      <p>
        Two independent apps: a Python trading engine (SMC + price action) and this
        Next.js dashboard. V1 focuses on signals and backtests before ML or live MT5.
      </p>
      <Link className="cta" href="/dashboard">
        Open dashboard
      </Link>
    </main>
  );
}
