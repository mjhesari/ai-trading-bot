"use client";

import type { Candle } from "@/types/market";

export function CandleChart({ candles }: { candles: Candle[] }) {
  if (!candles.length) {
    return <p className="muted">No candles loaded.</p>;
  }

  const slice = candles.slice(-120);
  const w = 900;
  const h = 360;
  const padX = 16;
  const padY = 20;
  const lows = slice.map((c) => c.low);
  const highs = slice.map((c) => c.high);
  const min = Math.min(...lows);
  const max = Math.max(...highs);
  const span = max - min || 1;
  const slot = (w - padX * 2) / slice.length;
  const bodyW = Math.max(2, slot * 0.55);

  const y = (price: number) => padY + ((max - price) / span) * (h - padY * 2);

  return (
    <div className="chart-stage">
      <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Candlestick chart">
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const yy = padY + t * (h - padY * 2);
          const price = max - t * span;
          return (
            <g key={t}>
              <line x1={padX} x2={w - padX} y1={yy} y2={yy} stroke="rgba(140,180,160,0.12)" />
              <text
                x={w - padX + 2}
                y={yy + 3}
                fill="#7f968a"
                fontSize="10"
                fontFamily="var(--font-mono)"
              >
                {price.toFixed(4)}
              </text>
            </g>
          );
        })}

        {slice.map((c, i) => {
          const x = padX + i * slot + slot / 2;
          const up = c.close >= c.open;
          const color = up ? "#3dcf8e" : "#ff6b6b";
          const yOpen = y(c.open);
          const yClose = y(c.close);
          const top = Math.min(yOpen, yClose);
          const bodyH = Math.max(1.5, Math.abs(yClose - yOpen));
          return (
            <g key={`${c.time}-${i}`}>
              <line x1={x} x2={x} y1={y(c.high)} y2={y(c.low)} stroke={color} strokeWidth="1.2" />
              <rect
                x={x - bodyW / 2}
                y={top}
                width={bodyW}
                height={bodyH}
                fill={color}
                opacity={0.92}
              />
            </g>
          );
        })}
      </svg>
    </div>
  );
}
