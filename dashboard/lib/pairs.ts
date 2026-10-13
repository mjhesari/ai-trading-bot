export const DEFAULT_PAIRS = [
  "EURUSD",
  "GBPUSD",
  "USDJPY",
  "USDCHF",
  "AUDUSD",
  "USDCAD",
  "NZDUSD",
  "EURGBP",
  "EURJPY",
  "GBPJPY",
  "AUDJPY",
  "EURAUD",
  "EURCHF",
  "GBPCHF",
  "XAUUSD",
  "SPX",
] as const;

const PAIR_LABELS: Record<string, string> = {
  SPX: "SPX · S&P 500",
  XAUUSD: "XAUUSD · Gold",
};

export function toPairOptions(pairs: string[]) {
  return pairs.map((p) => ({ value: p, label: PAIR_LABELS[p] ?? p }));
}
