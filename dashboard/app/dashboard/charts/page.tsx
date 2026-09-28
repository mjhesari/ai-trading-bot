"use client";

import dynamic from "next/dynamic";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FieldSelect } from "@/components/ui/field-select";
import { useChartMarket } from "@/hooks/use-chart-market";
import { roundPrice } from "@/lib/live-candle";
import { DATA_SOURCES, TIMEFRAMES } from "@/lib/timeframes";

const TradingChart = dynamic(
  () => import("@/components/charts/TradingChart").then((m) => m.TradingChart),
  { ssr: false, loading: () => <p className="muted">Loading chart…</p> },
);

function formatAgo(ts: number | null) {
  if (!ts) return "—";
  const sec = Math.max(0, Math.round((Date.now() - ts) / 1000));
  if (sec < 5) return "just now";
  if (sec < 60) return `${sec}s ago`;
  return `${Math.floor(sec / 60)}m ago`;
}

function priceDigits(symbol: string) {
  if (symbol.includes("JPY") || symbol.startsWith("XAU")) return 3;
  return 5;
}

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
    live,
    setLive,
    lastUpdated,
    livePulse,
    m1Count,
    pollMs,
  } = useChartMarket("EURUSD", "1h");

  const digits = priceDigits(symbol);
  const last = candles[candles.length - 1] ?? null;
  const prev = candles[candles.length - 2] ?? null;

  // All stats come from the same live forming candle the chart renders.
  const lastPrice = last ? roundPrice(last.close, symbol) : null;
  const openPrice = last ? roundPrice(last.open, symbol) : null;
  const highPrice = last ? roundPrice(last.high, symbol) : null;
  const lowPrice = last ? roundPrice(last.low, symbol) : null;
  const prevClose = prev ? roundPrice(prev.close, symbol) : null;

  const changeAbs =
    lastPrice != null && prevClose != null ? roundPrice(lastPrice - prevClose, symbol) : null;
  const changePct =
    changeAbs != null && prevClose ? (changeAbs / prevClose) * 100 : null;
  const fromOpen =
    lastPrice != null && openPrice != null ? roundPrice(lastPrice - openPrice, symbol) : null;
  const rangeAbs =
    highPrice != null && lowPrice != null ? roundPrice(highPrice - lowPrice, symbol) : null;
  const barsCount = candles.length;

  const pairOptions = pairs.map((p) => ({ value: p, label: p }));

  return (
    <main className="page chart-page">
      <div className="page-head">
        <div>
          <h1>Charts</h1>
          <p>Live OHLC with TradingView-style tools — crosshair, drawings, EMAs, volume.</p>
        </div>
        <div className="chart-head-actions">
          <Button
            variant={live ? "default" : "secondary"}
            onClick={() => setLive((v) => !v)}
          >
            {live ? "Live on" : "Live off"}
          </Button>
          <Button onClick={() => void refresh()} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </Button>
        </div>
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
        <Badge variant={live ? "default" : "secondary"}>
          {live ? `live ${(pollMs / 1000).toFixed(0)}s` : "paused"}
          {m1Count != null ? ` · ${m1Count}m1` : ""} · {formatAgo(lastUpdated)}
        </Badge>
      </div>

      <div className="grid-stats">
        <div className="stat-card">
          <div className="label">Last</div>
          <div
            className={`value${livePulse ? " tick" : ""}`}
            style={{
              color:
                fromOpen == null ? undefined : fromOpen >= 0 ? "var(--buy)" : "var(--sell)",
            }}
          >
            {lastPrice != null ? lastPrice.toFixed(digits) : "—"}
          </div>
          <div className="hint">
            {symbol} · {timeframe}
            {openPrice != null ? ` · O ${openPrice.toFixed(digits)}` : ""}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Change</div>
          <div
            className={`value${livePulse ? " tick" : ""}`}
            style={{ color: changeAbs != null && changeAbs >= 0 ? "var(--buy)" : "var(--sell)" }}
          >
            {changeAbs != null && changePct != null
              ? `${changeAbs >= 0 ? "+" : ""}${changeAbs.toFixed(digits)} (${changePct >= 0 ? "+" : ""}${changePct.toFixed(3)}%)`
              : "—"}
          </div>
          <div className="hint">
            vs prev close
            {fromOpen != null
              ? ` · from open ${fromOpen >= 0 ? "+" : ""}${fromOpen.toFixed(digits)}`
              : ""}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Range</div>
          <div className={`value${livePulse ? " tick" : ""}`}>
            {lowPrice != null && highPrice != null
              ? `${lowPrice.toFixed(digits)} – ${highPrice.toFixed(digits)}`
              : "—"}
          </div>
          <div className="hint">
            forming H−L
            {rangeAbs != null ? ` · ${rangeAbs.toFixed(digits)}` : ""}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Bars</div>
          <div className={`value${livePulse ? " tick" : ""}`}>{barsCount || "—"}</div>
          <div className="hint">
            history + live
            {m1Count != null ? ` · ${m1Count} × 1m in bar` : ""}
          </div>
        </div>
      </div>

      <div className="panel chart-panel">
        {error ? <p className="error">{error}</p> : null}
        {message ? <p className="muted chart-msg">{message}</p> : null}
        <TradingChart
          key={`${symbol}-${timeframe}`}
          candles={candles}
          symbol={symbol}
          viewKey={`${symbol}-${timeframe}`}
          live={live}
          livePulse={livePulse}
        />
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
