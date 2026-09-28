"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createChart,
  type IChartApi,
  type IPriceLine,
  type ISeriesApi,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import type { Candle } from "@/types/market";
import { ema, sma } from "@/lib/indicators";
import { roundPrice } from "@/lib/live-candle";

export type ChartTool = "cursor" | "hline" | "trend" | "measure";
export type IndicatorId = "volume" | "ema9" | "ema21" | "sma50";

type ChartBar = {
  time: UTCTimestamp;
  open: number;
  high: number;
  low: number;
  close: number;
};

type LinePoint = { time: UTCTimestamp; value: number };

function toChartBars(candles: Candle[], symbol: string): ChartBar[] {
  const byTime = new Map<number, ChartBar>();
  for (const c of candles) {
    const ms = Date.parse(c.time);
    if (Number.isNaN(ms)) continue;
    if (![c.open, c.high, c.low, c.close].every(Number.isFinite)) continue;
    const time = Math.floor(ms / 1000) as UTCTimestamp;
    byTime.set(time, {
      time,
      open: roundPrice(c.open, symbol),
      high: roundPrice(c.high, symbol),
      low: roundPrice(c.low, symbol),
      close: roundPrice(c.close, symbol),
    });
  }
  return Array.from(byTime.values()).sort((a, b) => a.time - b.time);
}

function linePoints(bars: ChartBar[], values: Array<number | null | undefined>): LinePoint[] {
  const out: LinePoint[] = [];
  for (let i = 0; i < bars.length; i++) {
    const v = values[i];
    if (typeof v !== "number" || !Number.isFinite(v)) continue;
    out.push({ time: bars[i].time, value: v });
  }
  return out;
}

/** lightweight-charts throws "Value is null" on bad internal state — never let it crash the page. */
function safeSetData<T>(series: { setData: (d: T[]) => void } | null | undefined, data: T[]) {
  if (!series) return;
  try {
    series.setData(data);
  } catch (err) {
    console.warn("chart setData skipped:", err);
  }
}

function safeUpdate<T>(series: { update: (d: T) => void } | null | undefined, data: T) {
  if (!series) return;
  try {
    series.update(data);
  } catch (err) {
    console.warn("chart update skipped:", err);
  }
}

function safeApplyOptions(
  series: { applyOptions: (o: Record<string, unknown>) => void } | null | undefined,
  options: Record<string, unknown>,
) {
  if (!series) return;
  try {
    series.applyOptions(options);
  } catch (err) {
    console.warn("chart applyOptions skipped:", err);
  }
}

function fmtPrice(n: number, digits: number) {
  return n.toFixed(digits);
}

function priceDigits(symbol: string) {
  if (symbol.includes("JPY") || symbol.startsWith("XAU")) return 3;
  return 5;
}

const INDICATOR_META: Record<IndicatorId, { label: string; color: string }> = {
  volume: { label: "Vol", color: "#5b8def" },
  ema9: { label: "EMA 9", color: "#f0c14a" },
  ema21: { label: "EMA 21", color: "#5ee0a8" },
  sma50: { label: "SMA 50", color: "#c084fc" },
};

export function TradingChart({
  candles,
  symbol,
  live = false,
  livePulse = false,
}: {
  candles: Candle[];
  symbol: string;
  viewKey?: string;
  live?: boolean;
  livePulse?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const ema9Ref = useRef<ISeriesApi<"Line"> | null>(null);
  const ema21Ref = useRef<ISeriesApi<"Line"> | null>(null);
  const sma50Ref = useRef<ISeriesApi<"Line"> | null>(null);
  const drawingSeriesRef = useRef<ISeriesApi<"Line">[]>([]);
  const hLinesRef = useRef<IPriceLine[]>([]);
  const trendDraftRef = useRef<LinePoint | null>(null);
  const measureDraftRef = useRef<LinePoint | null>(null);
  const readyRef = useRef(false);
  const toolRef = useRef<ChartTool>("cursor");
  const barsRef = useRef<ChartBar[]>([]);
  const prevSigRef = useRef("");
  const digitsRef = useRef(priceDigits(symbol));
  const hoveringRef = useRef(false);
  const symbolRef = useRef(symbol);

  const [tool, setTool] = useState<ChartTool>("cursor");
  const [indicators, setIndicators] = useState<Record<IndicatorId, boolean>>({
    volume: true,
    ema9: true,
    ema21: true,
    sma50: false,
  });
  const [hud, setHud] = useState<{
    o: number;
    h: number;
    l: number;
    c: number;
    change: number;
    cursor?: number | null;
  } | null>(null);
  const [measureLabel, setMeasureLabel] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  toolRef.current = tool;
  symbolRef.current = symbol;
  const digits = priceDigits(symbol);
  digitsRef.current = digits;

  const bars = useMemo(() => toChartBars(candles, symbol), [candles, symbol]);
  barsRef.current = bars;

  const last = bars[bars.length - 1];
  const prev = bars[bars.length - 2];
  const lastChange = last && prev ? last.close - prev.close : 0;

  useEffect(() => {
    // Only mirror last candle into HUD when mouse is NOT inspecting another bar.
    if (!last || hoveringRef.current) return;
    setHud({
      o: last.open,
      h: last.high,
      l: last.low,
      c: last.close,
      change: lastChange,
      cursor: null,
    });
  }, [last, lastChange]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      width: el.clientWidth,
      height: el.clientHeight || 480,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#8aa396",
        fontFamily: "JetBrains Mono, ui-monospace, monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "rgba(140,180,160,0.08)" },
        horzLines: { color: "rgba(140,180,160,0.08)" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: "rgba(94,224,168,0.45)",
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: "#1a2a24",
        },
        horzLine: {
          color: "rgba(94,224,168,0.45)",
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: "#1a2a24",
        },
      },
      rightPriceScale: {
        borderColor: "rgba(140,180,160,0.16)",
        scaleMargins: { top: 0.08, bottom: 0.18 },
      },
      timeScale: {
        borderColor: "rgba(140,180,160,0.16)",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 6,
      },
      handleScroll: { mouseWheel: true, pressedMouseMove: true },
      handleScale: { axisPressedMouseMove: true, mouseWheel: true, pinch: true },
    });

    const minMove = Number(`1e-${digitsRef.current}`);
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#3dcf8e",
      downColor: "#ff6b6b",
      borderUpColor: "#3dcf8e",
      borderDownColor: "#ff6b6b",
      wickUpColor: "#6be0ae",
      wickDownColor: "#ff8f8f",
      priceLineVisible: true,
      lastValueVisible: true,
      priceFormat: {
        type: "price",
        precision: digitsRef.current,
        minMove,
      },
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "vol",
      lastValueVisible: false,
      priceLineVisible: false,
    });
    chart.priceScale("vol").applyOptions({
      scaleMargins: { top: 0.82, bottom: 0 },
    });

    const mkLine = (color: string) =>
      chart.addSeries(LineSeries, {
        color,
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: false,
        priceFormat: {
          type: "price",
          precision: digitsRef.current,
          minMove,
        },
      });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;
    ema9Ref.current = mkLine(INDICATOR_META.ema9.color);
    ema21Ref.current = mkLine(INDICATOR_META.ema21.color);
    sma50Ref.current = mkLine(INDICATOR_META.sma50.color);
    readyRef.current = true;
    prevSigRef.current = "";

    const onCrosshair = (param: MouseEventParams<Time>) => {
      if (!param.point || param.time === undefined) {
        hoveringRef.current = false;
        const barsNow = barsRef.current;
        const lastBar = barsNow[barsNow.length - 1];
        const prevBar = barsNow[barsNow.length - 2];
        if (lastBar) {
          setHud({
            o: lastBar.open,
            h: lastBar.high,
            l: lastBar.low,
            c: lastBar.close,
            change: prevBar ? lastBar.close - prevBar.close : 0,
            cursor: null,
          });
        }
        return;
      }

      hoveringRef.current = true;
      const cursorPrice = candleSeries.coordinateToPrice(param.point.y);
      const bar = param.seriesData.get(candleSeries) as
        | { open: number; high: number; low: number; close: number; time: Time }
        | undefined;

      if (bar && typeof bar.open === "number") {
        const t = typeof bar.time === "number" ? bar.time : null;
        const idx =
          t == null ? -1 : barsRef.current.findIndex((b) => b.time === t);
        const p = idx > 0 ? barsRef.current[idx - 1] : undefined;
        const sym = symbolRef.current;
        setHud({
          o: roundPrice(bar.open, sym),
          h: roundPrice(bar.high, sym),
          l: roundPrice(bar.low, sym),
          c: roundPrice(bar.close, sym),
          change: p ? roundPrice(bar.close - p.close, sym) : 0,
          cursor:
            cursorPrice != null && Number.isFinite(cursorPrice)
              ? roundPrice(cursorPrice, sym)
              : null,
        });
        return;
      }

      if (cursorPrice != null && Number.isFinite(cursorPrice)) {
        setHud((prevHud) =>
          prevHud
            ? { ...prevHud, cursor: roundPrice(cursorPrice, symbolRef.current) }
            : prevHud,
        );
      }
    };
    chart.subscribeCrosshairMove(onCrosshair);

    const onClick = (param: MouseEventParams<Time>) => {
      const t = toolRef.current;
      if (t === "cursor" || !param.point || param.time === undefined) return;
      const price = candleSeries.coordinateToPrice(param.point.y);
      if (price === null || !Number.isFinite(price)) return;
      const time = param.time as UTCTimestamp;
      const point: LinePoint = { time, value: price };
      const d = digitsRef.current;

      if (t === "hline") {
        try {
          const line = candleSeries.createPriceLine({
            price,
            color: "rgba(94, 224, 168, 0.85)",
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: fmtPrice(price, d),
          });
          hLinesRef.current.push(line);
          setHint(`H-line @ ${fmtPrice(price, d)}`);
        } catch (err) {
          console.warn("hline failed:", err);
        }
        return;
      }

      if (t === "trend") {
        if (!trendDraftRef.current) {
          trendDraftRef.current = point;
          setHint("Trend: click second point");
          return;
        }
        const a = trendDraftRef.current;
        const b = point;
        trendDraftRef.current = null;
        const series = chart.addSeries(LineSeries, {
          color: "#5ee0a8",
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerVisible: false,
        });
        const pts = a.time <= b.time ? [a, b] : [b, a];
        safeSetData(series, pts);
        drawingSeriesRef.current.push(series);
        setHint(`Trend ${fmtPrice(a.value, d)} → ${fmtPrice(b.value, d)}`);
        return;
      }

      if (t === "measure") {
        if (!measureDraftRef.current) {
          measureDraftRef.current = point;
          setHint("Measure: click end point");
          setMeasureLabel(null);
          return;
        }
        const a = measureDraftRef.current;
        const b = point;
        measureDraftRef.current = null;
        const delta = b.value - a.value;
        const pct = a.value ? (delta / a.value) * 100 : 0;
        const series = chart.addSeries(LineSeries, {
          color: delta >= 0 ? "#3dcf8e" : "#ff6b6b",
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerVisible: true,
        });
        const pts = a.time <= b.time ? [a, b] : [b, a];
        safeSetData(series, pts);
        drawingSeriesRef.current.push(series);
        const label = `${delta >= 0 ? "+" : ""}${fmtPrice(delta, d)} (${pct >= 0 ? "+" : ""}${pct.toFixed(3)}%)`;
        setMeasureLabel(label);
        setHint(label);
      }
    };
    chart.subscribeClick(onClick);

    const ro = new ResizeObserver(() => {
      if (!containerRef.current || !chartRef.current) return;
      chartRef.current.applyOptions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight || 480,
      });
    });
    ro.observe(el);

    return () => {
      readyRef.current = false;
      ro.disconnect();
      try {
        chart.unsubscribeCrosshairMove(onCrosshair);
        chart.unsubscribeClick(onClick);
        chart.remove();
      } catch {
        // ignore teardown races
      }
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
      ema9Ref.current = null;
      ema21Ref.current = null;
      sma50Ref.current = null;
      drawingSeriesRef.current = [];
      hLinesRef.current = [];
    };
  }, []);

  useEffect(() => {
    if (!readyRef.current || !chartRef.current || !candleSeriesRef.current) return;
    if (!bars.length) return;

    const candleSeries = candleSeriesRef.current;
    const lastBar = bars[bars.length - 1];
    const closeVals = bars.map((b) => b.close);
    const ema9Pts = linePoints(bars, ema(closeVals, 9));
    const ema21Pts = linePoints(bars, ema(closeVals, 21));
    const sma50Pts = linePoints(bars, sma(closeVals, 50));

    const sig = `${bars.length}:${lastBar.time}:${lastBar.open}:${lastBar.high}:${lastBar.low}:${lastBar.close}:${indicators.volume}:${indicators.ema9}:${indicators.ema21}:${indicators.sma50}`;
    const prevSig = prevSigRef.current;
    const prevParts = prevSig.split(":");
    const sameShape =
      !!prevSig &&
      prevParts[0] === String(bars.length) &&
      prevParts[1] === String(lastBar.time) &&
      prevParts[6] === String(indicators.volume) &&
      prevParts[7] === String(indicators.ema9) &&
      prevParts[8] === String(indicators.ema21) &&
      prevParts[9] === String(indicators.sma50);
    const ohlcChanged =
      !prevSig ||
      prevParts[2] !== String(lastBar.open) ||
      prevParts[3] !== String(lastBar.high) ||
      prevParts[4] !== String(lastBar.low) ||
      prevParts[5] !== String(lastBar.close);
    const canTick = sameShape && ohlcChanged;

    if (canTick) {
      safeUpdate(candleSeries, lastBar);
      if (indicators.volume && volumeSeriesRef.current) {
        const c = candles[candles.length - 1];
        const volVal =
          c && Number.isFinite(c.volume) && c.volume > 0
            ? c.volume
            : Math.abs(lastBar.high - lastBar.low);
        if (Number.isFinite(volVal)) {
          safeUpdate(volumeSeriesRef.current, {
            time: lastBar.time,
            value: volVal,
            color:
              lastBar.close >= lastBar.open
                ? "rgba(61, 207, 142, 0.35)"
                : "rgba(255, 107, 107, 0.35)",
          });
        }
      }
      if (indicators.ema9 && ema9Pts.length) safeUpdate(ema9Ref.current, ema9Pts[ema9Pts.length - 1]);
      if (indicators.ema21 && ema21Pts.length) safeUpdate(ema21Ref.current, ema21Pts[ema21Pts.length - 1]);
      if (indicators.sma50 && sma50Pts.length) safeUpdate(sma50Ref.current, sma50Pts[sma50Pts.length - 1]);
    } else if (!sameShape || !prevSig) {
      safeSetData(candleSeries, bars);

      const volData: Array<{ time: UTCTimestamp; value: number; color: string }> = [];
      for (const c of candles) {
        const ms = Date.parse(c.time);
        if (Number.isNaN(ms)) continue;
        if (![c.open, c.high, c.low, c.close].every(Number.isFinite)) continue;
        const value =
          Number.isFinite(c.volume) && c.volume > 0 ? c.volume : Math.abs(c.high - c.low);
        if (!Number.isFinite(value)) continue;
        volData.push({
          time: Math.floor(ms / 1000) as UTCTimestamp,
          value,
          color:
            c.close >= c.open ? "rgba(61, 207, 142, 0.35)" : "rgba(255, 107, 107, 0.35)",
        });
      }
      safeSetData(volumeSeriesRef.current, volData);
      safeApplyOptions(volumeSeriesRef.current, { visible: indicators.volume });

      if (ema9Pts.length) safeSetData(ema9Ref.current, ema9Pts);
      safeApplyOptions(ema9Ref.current, { visible: indicators.ema9 && ema9Pts.length > 0 });

      if (ema21Pts.length) safeSetData(ema21Ref.current, ema21Pts);
      safeApplyOptions(ema21Ref.current, { visible: indicators.ema21 && ema21Pts.length > 0 });

      if (sma50Pts.length) safeSetData(sma50Ref.current, sma50Pts);
      safeApplyOptions(sma50Ref.current, { visible: indicators.sma50 && sma50Pts.length > 0 });

      // Fit only when series shape changes (new symbol/TF mount or bar count change)
      if (!prevSig || prevParts[0] !== String(bars.length)) {
        try {
          chartRef.current?.timeScale().fitContent();
        } catch {
          // ignore
        }
      }
    } else {
      // Indicator visibility toggles without OHLC change
      safeApplyOptions(volumeSeriesRef.current, { visible: indicators.volume });
      safeApplyOptions(ema9Ref.current, { visible: indicators.ema9 && ema9Pts.length > 0 });
      safeApplyOptions(ema21Ref.current, { visible: indicators.ema21 && ema21Pts.length > 0 });
      safeApplyOptions(sma50Ref.current, { visible: indicators.sma50 && sma50Pts.length > 0 });
    }

    safeApplyOptions(candleSeries, {
      priceLineColor: lastChange >= 0 ? "#3dcf8e" : "#ff6b6b",
      priceLineVisible: true,
      lastValueVisible: true,
      priceFormat: {
        type: "price",
        precision: digits,
        minMove: Number(`1e-${digits}`),
      },
    });

    prevSigRef.current = sig;
  }, [bars, candles, indicators, lastChange, live, digits]);

  const clearDrawings = () => {
    const chart = chartRef.current;
    const candleSeries = candleSeriesRef.current;
    for (const s of drawingSeriesRef.current) {
      try {
        chart?.removeSeries(s);
      } catch {
        // already removed
      }
    }
    drawingSeriesRef.current = [];
    if (candleSeries) {
      for (const line of hLinesRef.current) {
        try {
          candleSeries.removePriceLine(line);
        } catch {
          // already removed
        }
      }
    }
    hLinesRef.current = [];
    trendDraftRef.current = null;
    measureDraftRef.current = null;
    setMeasureLabel(null);
    setHint("Drawings cleared");
  };

  const toggleIndicator = (id: IndicatorId) => {
    setIndicators((prevState) => ({ ...prevState, [id]: !prevState[id] }));
  };

  const selectTool = (next: ChartTool) => {
    setTool(next);
    trendDraftRef.current = null;
    measureDraftRef.current = null;
    if (next === "hline") setHint("Click chart to place horizontal line");
    else if (next === "trend") setHint("Trend: click start, then end");
    else if (next === "measure") setHint("Measure: click two prices");
    else setHint(null);
  };

  return (
    <div className="tv-chart-shell">
      <div className="tv-toolbar" role="toolbar" aria-label="Chart tools">
        <div className="tv-tool-group">
          {(
            [
              ["cursor", "Cursor"],
              ["hline", "H-Line"],
              ["trend", "Trend"],
              ["measure", "Measure"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              className={`tv-tool${tool === id ? " active" : ""}`}
              onClick={() => selectTool(id)}
              title={label}
            >
              {label}
            </button>
          ))}
          <button type="button" className="tv-tool danger" onClick={clearDrawings}>
            Clear
          </button>
        </div>
        <div className="tv-tool-group">
          {(Object.keys(INDICATOR_META) as IndicatorId[]).map((id) => (
            <button
              key={id}
              type="button"
              className={`tv-tool indicator${indicators[id] ? " active" : ""}`}
              style={
                indicators[id]
                  ? { borderColor: INDICATOR_META[id].color, color: INDICATOR_META[id].color }
                  : undefined
              }
              onClick={() => toggleIndicator(id)}
            >
              {INDICATOR_META[id].label}
            </button>
          ))}
        </div>
        <div className="tv-live-pill">
          <span className={`tv-live-dot${live ? " on" : ""}${livePulse ? " pulse" : ""}`} />
          {live ? "LIVE" : "PAUSED"}
        </div>
      </div>

      <div className="tv-chart-wrap">
        <div className="tv-chart-watermark">{symbol}</div>
        {hud ? (
          <div className="tv-ohlc-hud" aria-live="polite">
            <span className="sym">{symbol}</span>
            <span>
              O <b>{fmtPrice(hud.o, digits)}</b>
            </span>
            <span>
              H <b>{fmtPrice(hud.h, digits)}</b>
            </span>
            <span>
              L <b>{fmtPrice(hud.l, digits)}</b>
            </span>
            <span>
              C{" "}
              <b style={{ color: hud.change >= 0 ? "var(--buy)" : "var(--sell)" }}>
                {fmtPrice(hud.c, digits)}
              </b>
            </span>
            <span style={{ color: hud.change >= 0 ? "var(--buy)" : "var(--sell)" }}>
              {hud.change >= 0 ? "+" : ""}
              {fmtPrice(hud.change, digits)}
            </span>
            {hud.cursor != null ? (
              <span>
                Y <b>{fmtPrice(hud.cursor, digits)}</b>
              </span>
            ) : null}
          </div>
        ) : null}
        {measureLabel ? <div className="tv-measure-badge">{measureLabel}</div> : null}
        <div ref={containerRef} className="tv-chart" />
      </div>
      {hint ? <p className="tv-hint muted">{hint}</p> : null}
    </div>
  );
}
