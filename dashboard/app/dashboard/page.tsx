"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { useSignals } from "@/hooks/use-signals";
import { getHealth } from "@/services/trading-engine";

export default function DashboardPage() {
  const { signals, loading, error, source } = useSignals("EURUSD", "1h");
  const [engineOk, setEngineOk] = useState<boolean | null>(null);
  const [dataSource, setDataSource] = useState<string>("yahoo");

  useEffect(() => {
    getHealth()
      .then((h) => {
        setEngineOk(true);
        setDataSource(h.dataSource || "yahoo");
      })
      .catch(() => setEngineOk(false));
  }, []);

  const stats = useMemo(() => {
    const buys = signals.filter((s) => s.direction === "BUY").length;
    const sells = signals.filter((s) => s.direction === "SELL").length;
    const avgConf =
      signals.length > 0
        ? Math.round(signals.reduce((a, s) => a + s.confidence, 0) / signals.length)
        : 0;
    return { buys, sells, avgConf, total: signals.length };
  }, [signals]);

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <h1>Overview</h1>
          <p>Mac-ready desk on real Yahoo market data — charts, signals, and backtests.</p>
        </div>
        <Button asChild>
          <Link href="/dashboard/charts">Open charts</Link>
        </Button>
      </div>

      <div className="grid-stats">
        <div className="stat-card">
          <div className="label">Engine</div>
          <div className="value" style={{ color: engineOk ? "var(--buy)" : "var(--sell)" }}>
            {engineOk === null ? "…" : engineOk ? "UP" : "DOWN"}
          </div>
          <div className="hint">config · {dataSource}</div>
        </div>
        <div className="stat-card">
          <div className="label">Feed</div>
          <div className="value" style={{ fontSize: "1.2rem" }}>
            {source || "yahoo"}
          </div>
          <div className="hint">live API source</div>
        </div>
        <div className="stat-card">
          <div className="label">Signals</div>
          <div className="value">{loading ? "…" : stats.total}</div>
          <div className="hint">
            <span className="buy">{stats.buys}B</span> / <span className="sell">{stats.sells}S</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Avg conf</div>
          <div className="value">{stats.avgConf || "—"}</div>
          <div className="hint">confluence score</div>
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="quick-links">
        <Link className="quick-card" href="/dashboard/signals">
          <h3>Signal feed</h3>
          <p>Real-data BUY/SELL setups with entry, stop, and targets.</p>
        </Link>
        <Link className="quick-card" href="/dashboard/charts">
          <h3>Candle charts</h3>
          <p>TradingView-style candles for every pair in the watchlist.</p>
        </Link>
        <Link className="quick-card" href="/dashboard/backtest">
          <h3>Backtest</h3>
          <p>Replay SMC on Yahoo history and inspect expectancy.</p>
        </Link>
        <Link className="quick-card" href="/dashboard/settings">
          <h3>Deploy settings</h3>
          <p>Vercel dashboard + VPS engine wiring.</p>
        </Link>
      </div>
    </main>
  );
}
