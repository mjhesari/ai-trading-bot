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
};

export type SignalsResponse = {
  symbol: string;
  timeframe: string;
  count: number;
  signals: TradingSignal[];
};
