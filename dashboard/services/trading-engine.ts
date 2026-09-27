import { apiGet, apiPost, ENGINE_URL } from "@/lib/api";
import type { BacktestReport, BacktestRequest } from "@/types/backtest";
import type { MarketResponse } from "@/types/market";
import type { SignalsResponse } from "@/types/signal";

export { ENGINE_URL };

export function getHealth() {
  return apiGet<{ status: string }>("/api/health");
}

export function getSignals(params?: {
  symbol?: string;
  timeframe?: string;
  useSample?: boolean;
}) {
  const q = new URLSearchParams();
  if (params?.symbol) q.set("symbol", params.symbol);
  if (params?.timeframe) q.set("timeframe", params.timeframe);
  q.set("use_sample", String(params?.useSample ?? true));
  return apiGet<SignalsResponse>(`/api/signals?${q.toString()}`);
}

export function getMarket(symbol: string, useSample = true) {
  const q = new URLSearchParams({ use_sample: String(useSample) });
  return apiGet<MarketResponse>(`/api/market/${encodeURIComponent(symbol)}?${q}`);
}

export function runBacktest(body: BacktestRequest) {
  return apiPost<BacktestReport>("/api/backtest", body);
}

export function getBacktest(id: string) {
  return apiGet<BacktestReport>(`/api/backtest/${id}`);
}
