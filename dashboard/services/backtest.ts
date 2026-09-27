import { getBacktest, runBacktest } from "@/services/trading-engine";
import type { BacktestRequest } from "@/types/backtest";

export async function startBacktest(body: BacktestRequest) {
  return runBacktest(body);
}

export async function loadBacktest(id: string) {
  return getBacktest(id);
}
