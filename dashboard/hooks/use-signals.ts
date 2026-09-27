"use client";

import { useCallback, useEffect, useState } from "react";
import { getSignals } from "@/services/trading-engine";
import type { TradingSignal } from "@/types/signal";

export function useSignals() {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSignals({ useSample: true });
      setSignals(data.signals);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load signals");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { signals, loading, error, refresh };
}
