"use client";

import dynamic from "next/dynamic";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FieldSelect } from "@/components/ui/field-select";
import { useChartMarket } from "@/hooks/use-chart-market";
import { DATA_SOURCES, TIMEFRAMES } from "@/lib/timeframes";

const TradingChart = dynamic(
  () => import("@/components/charts/TradingChart").then((m) => m.TradingChart),
  { ssr: false, loading: () => <p className="muted">Loading chart…</p> },
);

export default function ChartsPage() {
  const {
    symbol,
    setSymbol,
    timeframe,
    setTimeframe,
    source,
    setSource,
    pairs,
    candles,
    dataSource,
    message,
    loading,
    error,
    refresh,
  } = useChartMarket("EURUSD", "1h");

  const last = candles[candles.length - 1];
  const prev = candles[candles.length - 2];
  const change = last && prev ? last.close - prev.close : 0;
  const changePct = last && prev && prev.close ? (change / prev.close) * 100 : 0;
  const pairOptions = pairs.map((p) => ({ value: p, label: p }));

  return (
    <main className="page chart-page">
      <div className="page-head">
        <div>
          <h1>Charts</h1>
          <p>Full timeframe set with live OHLC — deep-blue desk.</p>
        </div>
        <Button onClick={() => void refresh()} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="panel toolbar-grid">
        <FieldSelect label="Pair" value={symbol} onValueChange={setSymbol} options={pairOptions} />
        <FieldSelect
          label="Timeframe"
          value={timeframe}
          onValueChange={setTimeframe}
          options={TIMEFRAMES.map((t) => ({ value: t.value, label: t.label }))}
        />
        <FieldSelect
          label="Source"
          value={source}
          onValueChange={setSource}
          options={DATA_SOURCES.map((s) => ({ value: s.value, label: s.label }))}
        />
        <Badge variant={dataSource === "twelvedata" || dataSource === "yahoo" ? "default" : "secondary"}>
          {dataSource || "…"}
        </Badge>
      </div>

      <div className="grid-stats">
        <div className="stat-card">
          <div className="label">Last</div>
          <div className="value">
            {last
              ? last.close.toFixed(symbol.includes("JPY") || symbol.startsWith("XAU") ? 3 : 5)
              : "—"}
          </div>
          <div className="hint">
            {symbol} · {timeframe}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Change</div>
          <div className="value" style={{ color: change >= 0 ? "var(--buy)" : "var(--sell)" }}>
            {last ? `${change >= 0 ? "+" : ""}${changePct.toFixed(3)}%` : "—"}
          </div>
          <div className="hint">vs previous bar</div>
        </div>
        <div className="stat-card">
          <div className="label">High</div>
          <div className="value">{last ? last.high.toFixed(5) : "—"}</div>
          <div className="hint">bar high</div>
        </div>
        <div className="stat-card">
          <div className="label">Bars</div>
          <div className="value">{candles.length || "—"}</div>
          <div className="hint">loaded</div>
        </div>
      </div>

      <div className="panel chart-panel">
        {error ? <p className="error">{error}</p> : null}
        {message ? <p className="muted chart-msg">{message}</p> : null}
        <TradingChart candles={candles} symbol={symbol} />
        <div className="pair-chips">
          {pairs.slice(0, 15).map((p) => (
            <button
              key={p}
              type="button"
              className={`chip${p === symbol ? " active" : ""}`}
              onClick={() => setSymbol(p)}
            >
              {p}
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
