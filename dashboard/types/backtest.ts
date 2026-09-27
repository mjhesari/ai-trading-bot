export type BacktestMetrics = {
  totalTrades: number;
  wins?: number;
  losses?: number;
  winRate: number;
  profitFactor: number;
  expectancy: number;
  maxDrawdown: number;
  averageR: number;
  sharpe: number;
  finalBalance: number;
  netProfit: number;
  returnPct: number;
  equityCurve: number[];
};

export type BacktestReport = {
  id: string;
  symbol: string;
  timeframe: string;
  createdAt: string;
  source?: string;
  message?: string | null;
  bars?: number;
  metrics: BacktestMetrics;
  trades: Array<Record<string, unknown>>;
};

export type BacktestRequest = {
  symbol: string;
  timeframe: string;
  useSample?: boolean;
  source?: string;
  sampleN?: number;
};
