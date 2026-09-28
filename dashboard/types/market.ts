export type Candle = {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type MarketResponse = {
  symbol: string;
  timeframe: string;
  source: "mt5" | "yahoo" | "sample" | string;
  message?: string | null;
  count: number;
  candles: Candle[];
  livePrice?: number | null;
};

export type QuoteResponse = {
  symbol: string;
  price: number;
  asOf?: string | null;
  source: string;
  ts: number;
  barOpenMs?: number;
  timeframe?: string;
  m1Count?: number;
  forming?: {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  };
};

export type PairsResponse = {
  source: string;
  pairs: string[];
  details?: Array<Record<string, unknown>>;
  message?: string;
};

export type Mt5Status = {
  available: boolean;
  connected: boolean;
  platform: string;
  error?: string | null;
  login?: number | null;
  server?: string | null;
  terminal?: Record<string, unknown>;
  account?: {
    login: number;
    name: string;
    server: string;
    currency: string;
    balance: number;
    equity: number;
    margin: number;
    leverage: number;
  };
};
