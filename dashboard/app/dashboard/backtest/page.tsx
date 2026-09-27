"use client";

import { FormEvent, useState } from "react";
import { MetricsPanel } from "@/components/backtest/MetricsPanel";
import { useBacktest } from "@/hooks/use-backtest";

export default function BacktestPage() {
  const { report, loading, error, run } = useBacktest();
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("1h");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await run({ symbol, timeframe, useSample: true, sampleN: 800 });
  }

  return (
    <main className="page">
      <h1>Backtest</h1>
      <p className="muted">Runs SMC V1 against sample OHLC via FastAPI.</p>
      <div className="panel">
        <form className="form" onSubmit={(e) => void onSubmit(e)}>
          <label>
            Symbol
            <input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          </label>
          <label>
            Timeframe
            <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
              <option value="15m">15m</option>
              <option value="1h">1h</option>
              <option value="4h">4h</option>
              <option value="1d">1d</option>
            </select>
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Running…" : "Run backtest"}
          </button>
        </form>
        {error ? <p className="error">{error}</p> : null}
        {report ? (
          <>
            <p className="muted">ID: {report.id}</p>
            <MetricsPanel metrics={report.metrics} />
          </>
        ) : null}
      </div>
    </main>
  );
}
