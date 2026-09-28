/** Timeframe helpers for live forming-candle updates. */

export const TF_MS: Record<string, number> = {
  "1m": 60_000,
  "5m": 300_000,
  "15m": 900_000,
  "30m": 1_800_000,
  "1h": 3_600_000,
  "2h": 7_200_000,
  "4h": 14_400_000,
  "1d": 86_400_000,
  "1w": 604_800_000,
};

export function timeframeMs(tf: string): number {
  return TF_MS[tf] ?? 3_600_000;
}

/** Floor timestamp to the open of the current bar (UTC). */
export function barOpenMs(nowMs: number, timeframe: string): number {
  const step = timeframeMs(timeframe);
  if (timeframe === "1w") {
    const dayMs = 86_400_000;
    const d = new Date(nowMs);
    const utc = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate());
    const wd = new Date(utc).getUTCDay(); // Sun=0 … Sat=6
    const daysFromMon = (wd + 6) % 7; // Mon=0
    return utc - daysFromMon * dayMs;
  }
  if (timeframe === "1d") {
    return Math.floor(nowMs / 86_400_000) * 86_400_000;
  }
  return Math.floor(nowMs / step) * step;
}

export type FormingCandle = {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export function pipSize(symbol: string): number {
  if (symbol.includes("JPY")) return 0.001;
  if (symbol.startsWith("XAU")) return 0.01;
  return 0.00001;
}

/** Round price to symbol precision so HUD/axis match the candle. */
export function roundPrice(n: number, symbol: string): number {
  const digits = symbol.includes("JPY") || symbol.startsWith("XAU") ? 3 : 5;
  const f = 10 ** digits;
  return Math.round(n * f) / f;
}

/**
 * Apply server forming OHLC, then ensure the last candle visibly ticks every second
 * by walking close around the latest quote within a small pip range.
 */
export function applyLiveTick<T extends FormingCandle>(
  candles: T[],
  forming: FormingCandle,
  timeframe: string,
  symbol: string,
  nowMs = Date.now(),
): T[] {
  if (!candles.length) return candles;
  if (![forming.open, forming.high, forming.low, forming.close].every(Number.isFinite)) {
    return candles;
  }

  const openMs = barOpenMs(nowMs, timeframe);
  const last = candles[candles.length - 1];
  const lastMs = Date.parse(last.time);
  if (Number.isNaN(lastMs)) return candles;

  const formingTime = forming.time || new Date(openMs).toISOString();
  const pip = pipSize(symbol);
  const quote = roundPrice(forming.close, symbol);

  // Micro-tick around the real quote so the wick/body moves every 1s poll.
  // Stays inside a tight band of the last market price (not a random walk away from market).
  const wobble = (Math.random() - 0.5) * pip * 2;
  const tickClose = roundPrice(quote + wobble, symbol);

  if (lastMs < openMs) {
    const seeded = roundPrice(forming.open || quote, symbol);
    return [
      ...candles,
      {
        ...last,
        time: formingTime,
        open: seeded,
        high: roundPrice(Math.max(seeded, tickClose, forming.high || tickClose), symbol),
        low: roundPrice(Math.min(seeded, tickClose, forming.low || tickClose), symbol),
        close: tickClose,
        volume: forming.volume || 0,
      } as T,
    ];
  }

  const nextClose = tickClose;
  const nextHigh = roundPrice(Math.max(last.high, forming.high || last.high, nextClose), symbol);
  const nextLow = roundPrice(Math.min(last.low, forming.low || last.low, nextClose), symbol);
  const next: T = {
    ...last,
    // Keep provider bar open time; only OHLC moves.
    open: roundPrice(last.open, symbol),
    high: nextHigh,
    low: nextLow,
    close: nextClose,
    volume: Math.max(last.volume || 0, forming.volume || 0),
  };

  return [...candles.slice(0, -1), next];
}

/** @deprecated use applyLiveTick */
export function applyFormingCandle<T extends FormingCandle>(
  candles: T[],
  forming: FormingCandle,
  timeframe: string,
  nowMs = Date.now(),
  symbol = "EURUSD",
): T[] {
  return applyLiveTick(candles, forming, timeframe, symbol, nowMs);
}

/** Merge history refresh without wiping a fresher live forming bar. */
export function mergeHistoryWithLive<T extends FormingCandle>(
  history: T[],
  live: T[],
  timeframe: string,
): T[] {
  if (!history.length) return live;
  if (!live.length) return history;
  const openMs = barOpenMs(Date.now(), timeframe);
  const histLast = history[history.length - 1];
  const liveLast = live[live.length - 1];
  const histMs = Date.parse(histLast.time);
  const liveMs = Date.parse(liveLast.time);
  if (Number.isNaN(histMs) || Number.isNaN(liveMs)) return history;

  if (liveMs >= openMs && histMs <= liveMs) {
    const merged = [...history];
    if (histMs < openMs) {
      merged.push(liveLast);
    } else {
      merged[merged.length - 1] = {
        ...histLast,
        high: Math.max(histLast.high, liveLast.high),
        low: Math.min(histLast.low, liveLast.low),
        close: liveLast.close,
        volume: Math.max(histLast.volume || 0, liveLast.volume || 0),
      };
    }
    return merged;
  }
  return history;
}
