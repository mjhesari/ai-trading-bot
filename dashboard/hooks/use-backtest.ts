"use client";

import { useCallback, useState } from "react";
import { runBacktest } from "@/services/trading-engine";
import type { BacktestReport, BacktestRequest } from "@/types/backtest";

export function useBacktest() {
  const [report, setReport] = useState<BacktestReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (body: BacktestRequest) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runBacktest(body);
      setReport(data);
      return data;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backtest failed");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { report, loading, error, run };
}
