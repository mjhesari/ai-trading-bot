export const TIMEFRAMES = [
  { value: "1m", label: "1m · 1 Minute" },
  { value: "5m", label: "5m · 5 Minutes" },
  { value: "15m", label: "15m · 15 Minutes" },
  { value: "30m", label: "30m · 30 Minutes" },
  { value: "1h", label: "1h · 1 Hour" },
  { value: "2h", label: "2h · 2 Hours" },
  { value: "4h", label: "4h · 4 Hours" },
  { value: "1d", label: "1d · Daily" },
  { value: "1w", label: "1w · Weekly" },
] as const;

export type TimeframeValue = (typeof TIMEFRAMES)[number]["value"];

export const DATA_SOURCES = [
  { value: "yahoo", label: "Yahoo Finance" },
  { value: "twelvedata", label: "Twelve Data" },
  { value: "auto", label: "Auto" },
  { value: "sample", label: "Sample (demo)" },
] as const;
