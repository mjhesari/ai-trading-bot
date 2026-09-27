"use client";

import { useCallback, useEffect, useState } from "react";
import { getMarket, getPairs } from "@/services/trading-engine";
import { useEngineSource } from "@/hooks/use-engine-source";
import type { Candle } from "@/types/market";

export function useChartMarket(initialSymbol = "EURUSD", initialTf = "1h") {
  const { source, setSource, ready } = useEngineSource("yahoo");
  const [symbol, setSymbol] = useState(initialSymbol);
  const [timeframe, setTimeframe] = useState(initialTf);
  const [pairs, setPairs] = useState<string[]>([initialSymbol]);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [dataSource, setDataSource] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPairs = useCallback(async () => {
    try {
      const data = await getPairs();
      if (data.pairs?.length) setPairs(data.pairs);
    } catch {
      // keep defaults
    }
  }, []);

  const refresh = useCallback(async () => {
    if (!ready) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getMarket(symbol, {
        timeframe,
        source,
        count: 800,
      });
      setCandles(data.candles);
      setDataSource(data.source);
      setMessage(data.message ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load market");
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe, source, ready]);

  useEffect(() => {
    void loadPairs();
  }, [loadPairs]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
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
  };
}
