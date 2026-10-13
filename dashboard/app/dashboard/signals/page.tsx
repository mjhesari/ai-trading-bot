"use client";

import { useState } from "react";
import { SignalTable } from "@/components/signals/SignalTable";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FieldSelect } from "@/components/ui/field-select";
import { useSignals } from "@/hooks/use-signals";
import { STRATEGIES } from "@/lib/strategies";
import { TIMEFRAMES } from "@/lib/timeframes";

const PAIRS = [
  { value: "EURUSD", label: "EURUSD" },
  { value: "GBPUSD", label: "GBPUSD" },
  { value: "USDJPY", label: "USDJPY" },
  { value: "AUDUSD", label: "AUDUSD" },
  { value: "USDCAD", label: "USDCAD" },
  { value: "XAUUSD", label: "XAUUSD" },
  { value: "SPX", label: "SPX · S&P 500" },
  { value: "EURJPY", label: "EURJPY" },
  { value: "GBPJPY", label: "GBPJPY" },
];

export default function SignalsPage() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("1h");
  const [strategy, setStrategy] = useState("smc");
  const { signals, loading, error, refresh, source, message, bars, stats } = useSignals(
    symbol,
    timeframe,
    strategy,
  );

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <h1>Signals</h1>
          <p>BUY/SELL from SMC or ICT — entry, SL, TP, then graded vs later bars.</p>
        </div>
        <Button onClick={() => void refresh()} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="panel toolbar-grid">
        <FieldSelect
          label="Strategy"
          value={strategy}
          onValueChange={setStrategy}
          options={STRATEGIES.map((s) => ({ value: s.value, label: s.label }))}
        />
        <FieldSelect label="Pair" value={symbol} onValueChange={setSymbol} options={PAIRS} />
        <FieldSelect
          label="Timeframe"
          value={timeframe}
          onValueChange={setTimeframe}
          options={TIMEFRAMES.map((t) => ({ value: t.value, label: t.label }))}
        />
        <Badge>{source || "…"}</Badge>
      </div>

      <div className="grid-stats">
        <div className="stat-card">
          <div className="label">Win rate</div>
          <div className="value">
            {stats?.winRate != null ? `${Math.round(stats.winRate * 100)}%` : "—"}
          </div>
          <div className="hint">closed setups only</div>
        </div>
        <div className="stat-card">
          <div className="label">Correct</div>
          <div className="value" style={{ color: "var(--buy)" }}>
            {stats?.wins ?? "—"}
          </div>
          <div className="hint">TP hit before SL</div>
        </div>
        <div className="stat-card">
          <div className="label">Wrong</div>
          <div className="value" style={{ color: "var(--sell)" }}>
            {stats?.losses ?? "—"}
          </div>
          <div className="hint">SL hit first</div>
        </div>
        <div className="stat-card">
          <div className="label">Open</div>
          <div className="value">{stats?.open ?? "—"}</div>
          <div className="hint">not resolved yet</div>
        </div>
      </div>

      <div className="panel">
        <h2 className="panel-title">
          Setups
          {bars != null ? <span className="muted"> · {bars} bars</span> : null}
        </h2>
        {message ? <p className="muted chart-msg">{message}</p> : null}
        {error ? <p className="error">{error}</p> : null}
        {loading && !signals.length ? <p className="muted">Fetching market data…</p> : null}
        {!loading || signals.length ? <SignalTable signals={signals} /> : null}
      </div>
    </main>
  );
}
