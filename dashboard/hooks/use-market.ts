"use client";

import { useCallback, useState } from "react";
import { getMarket } from "@/services/trading-engine";
import type { Candle } from "@/types/market";

export function useMarket(symbol = "EURUSD") {
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMarket(symbol, { source: "auto", count: 500 });
      setCandles(data.candles);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load market");
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  return { candles, loading, error, refresh };
}
