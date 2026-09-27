"use client";

import { useCallback, useEffect, useState } from "react";
import { getSignals } from "@/services/trading-engine";
import { useEngineSource } from "@/hooks/use-engine-source";
import type { TradingSignal } from "@/types/signal";

export function useSignals(symbol = "EURUSD", timeframe = "1h") {
  const { source: engineSource, ready } = useEngineSource("yahoo");
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);
  const [bars, setBars] = useState<number | null>(null);

  const refresh = useCallback(async () => {
    if (!ready) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getSignals({ symbol, timeframe, source: engineSource });
      setSignals(data.signals);
      setSource(data.source ?? engineSource);
      setMessage(data.message ?? null);
      setBars(data.bars ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load signals");
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe, engineSource, ready]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { signals, loading, error, refresh, source, message, bars };
}
