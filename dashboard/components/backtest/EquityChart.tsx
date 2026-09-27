"use client";

export function EquityChart({ points }: { points: number[] }) {
  if (!points.length) return null;

  const w = 640;
  const h = 160;
  const pad = 8;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;

  const coords = points.map((v, i) => {
    const x = pad + (i / Math.max(points.length - 1, 1)) * (w - pad * 2);
    const y = h - pad - ((v - min) / span) * (h - pad * 2);
    return `${x},${y}`;
  });

  const line = coords.join(" ");
  const area = `${pad},${h - pad} ${line} ${w - pad},${h - pad}`;
  const up = points[points.length - 1] >= points[0];

  return (
    <svg className="equity-chart" viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Equity curve">
      <defs>
        <linearGradient id="eqFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={up ? "#5ee0a8" : "#ff6b6b"} stopOpacity="0.35" />
          <stop offset="100%" stopColor={up ? "#5ee0a8" : "#ff6b6b"} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={area} fill="url(#eqFill)" />
      <polyline
        points={line}
        fill="none"
        stroke={up ? "#5ee0a8" : "#ff6b6b"}
        strokeWidth="2.2"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}
