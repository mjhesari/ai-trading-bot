"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";
import type { Candle } from "@/types/market";

function toChartBars(candles: Candle[]) {
  const byTime = new Map<number, { time: UTCTimestamp; open: number; high: number; low: number; close: number }>();

  for (const c of candles) {
    const ms = Date.parse(c.time);
    if (Number.isNaN(ms)) continue;
    const time = Math.floor(ms / 1000) as UTCTimestamp;
    // Keep last bar for duplicate timestamps (lightweight-charts requires unique ascending times)
    byTime.set(time, {
      time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    });
  }

  return Array.from(byTime.values()).sort((a, b) => a.time - b.time);
}

export function TradingChart({
  candles,
  symbol,
}: {
  candles: Candle[];
  symbol: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      width: el.clientWidth,
      height: el.clientHeight || 420,
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
          style: 2,
          labelBackgroundColor: "#1a2a24",
        },
        horzLine: {
          color: "rgba(94,224,168,0.45)",
          width: 1,
          style: 2,
          labelBackgroundColor: "#1a2a24",
        },
      },
      rightPriceScale: {
        borderColor: "rgba(140,180,160,0.16)",
        scaleMargins: { top: 0.08, bottom: 0.12 },
      },
      timeScale: {
        borderColor: "rgba(140,180,160,0.16)",
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: { mouseWheel: true, pressedMouseMove: true },
      handleScale: { axisPressedMouseMove: true, mouseWheel: true, pinch: true },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#3dcf8e",
      downColor: "#ff6b6b",
      borderUpColor: "#3dcf8e",
      borderDownColor: "#ff6b6b",
      wickUpColor: "#6be0ae",
      wickDownColor: "#ff8f8f",
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const ro = new ResizeObserver(() => {
      if (!containerRef.current || !chartRef.current) return;
      chartRef.current.applyOptions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight || 420,
      });
    });
    ro.observe(el);

    return () => {
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current || !chartRef.current) return;
    const bars = toChartBars(candles);
    seriesRef.current.setData(bars);
    if (bars.length) {
      chartRef.current.timeScale().fitContent();
    }
  }, [candles, symbol]);

  return (
    <div className="tv-chart-wrap">
      <div className="tv-chart-watermark">{symbol}</div>
      <div ref={containerRef} className="tv-chart" />
    </div>
  );
}
