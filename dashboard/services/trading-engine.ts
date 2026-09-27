import { apiGet, apiPost, apiPut, ENGINE_URL } from "@/lib/api";
import type { BacktestReport, BacktestRequest } from "@/types/backtest";
import type { MarketResponse, Mt5Status, PairsResponse } from "@/types/market";
import type { EngineSettings, SettingsUpdate, SourceTestResult } from "@/types/settings";
import type { SignalsResponse } from "@/types/signal";

export { ENGINE_URL };

export function getHealth() {
  return apiGet<{
    status: string;
    dataSource?: string;
    providers?: Record<string, boolean>;
    pairs?: string[];
    settings?: EngineSettings;
  }>("/api/health");
}

export function getEngineSettings() {
  return apiGet<EngineSettings>("/api/settings");
}

export function updateEngineSettings(body: SettingsUpdate) {
  return apiPut<EngineSettings>("/api/settings", body);
}

export function testEngineSource(symbol = "EURUSD", timeframe = "1h") {
  const q = new URLSearchParams({ symbol, timeframe });
  return apiPost<SourceTestResult>(`/api/settings/test-source?${q.toString()}`, {});
}

export function getSignals(params?: {
  symbol?: string;
  timeframe?: string;
  source?: string;
  useSample?: boolean;
}) {
  const q = new URLSearchParams();
  if (params?.symbol) q.set("symbol", params.symbol);
  if (params?.timeframe) q.set("timeframe", params.timeframe);
  if (params?.source) q.set("source", params.source);
  else if (params?.useSample !== undefined) q.set("use_sample", String(params.useSample));
  return apiGet<SignalsResponse>(`/api/signals?${q.toString()}`);
}

export function getMarket(
  symbol: string,
  opts?: { timeframe?: string; source?: string; count?: number },
) {
  const q = new URLSearchParams();
  if (opts?.timeframe) q.set("timeframe", opts.timeframe);
  if (opts?.source) q.set("source", opts.source);
  if (opts?.count) q.set("count", String(opts.count));
  const qs = q.toString();
  return apiGet<MarketResponse>(`/api/market/${encodeURIComponent(symbol)}${qs ? `?${qs}` : ""}`);
}

export function getPairs() {
  return apiGet<PairsResponse>("/api/market/pairs");
}

export function getMt5Status() {
  return apiGet<Mt5Status>("/api/mt5/status");
}

export function connectMt5(body?: {
  login?: number;
  password?: string;
  server?: string;
  path?: string;
}) {
  return apiPost<Mt5Status>("/api/mt5/connect", body ?? {});
}

export function disconnectMt5() {
  return apiPost<{ connected: boolean }>("/api/mt5/disconnect", {});
}

export function runBacktest(body: BacktestRequest) {
  return apiPost<BacktestReport>("/api/backtest", body);
}

export function getBacktest(id: string) {
  return apiGet<BacktestReport>(`/api/backtest/${id}`);
}
