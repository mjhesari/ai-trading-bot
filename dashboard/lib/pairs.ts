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
] as const;

export function toPairOptions(pairs: string[]) {
  return pairs.map((p) => ({ value: p, label: p }));
}
