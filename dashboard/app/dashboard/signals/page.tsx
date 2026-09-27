"use client";

import { useState } from "react";
import { SignalTable } from "@/components/signals/SignalTable";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FieldSelect } from "@/components/ui/field-select";
import { useSignals } from "@/hooks/use-signals";
import { TIMEFRAMES } from "@/lib/timeframes";

const PAIRS = [
  { value: "EURUSD", label: "EURUSD" },
  { value: "GBPUSD", label: "GBPUSD" },
  { value: "USDJPY", label: "USDJPY" },
  { value: "AUDUSD", label: "AUDUSD" },
  { value: "USDCAD", label: "USDCAD" },
  { value: "XAUUSD", label: "XAUUSD" },
  { value: "EURJPY", label: "EURJPY" },
  { value: "GBPJPY", label: "GBPJPY" },
];

export default function SignalsPage() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("1h");
  const { signals, loading, error, refresh, source, message, bars } = useSignals(symbol, timeframe);

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <h1>Signals</h1>
          <p>BUY/SELL from SMC across all timeframes on real market OHLC.</p>
        </div>
        <Button onClick={() => void refresh()} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="panel toolbar-grid">
        <FieldSelect label="Pair" value={symbol} onValueChange={setSymbol} options={PAIRS} />
        <FieldSelect
          label="Timeframe"
          value={timeframe}
          onValueChange={setTimeframe}
          options={TIMEFRAMES.map((t) => ({ value: t.value, label: t.label }))}
        />
        <Badge>{source || "…"}</Badge>
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
