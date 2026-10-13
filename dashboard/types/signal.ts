export type TradingSignal = {
  symbol: string;
  timeframe: string;
  direction: "BUY" | "SELL" | string;
  entry: number;
  stopLoss: number;
  takeProfit1: number;
  takeProfit2: number;
  riskReward: number;
  confidence: number;
  reasons: string[];
  time?: string | null;
  outcome?: "OPEN" | "SL" | "TP1" | "TP2" | string | null;
  correct?: boolean | null;
  exitPrice?: number | null;
  exitTime?: string | null;
  barsHeld?: number | null;
  rMultiple?: number | null;
};

export type SignalStats = {
  total: number;
  wins: number;
  losses: number;
  open: number;
  winRate: number | null;
};

export type SignalsResponse = {
  symbol: string;
  timeframe: string;
  source?: string;
  message?: string | null;
  bars?: number;
  count: number;
  stats?: SignalStats;
  signals: TradingSignal[];
};
