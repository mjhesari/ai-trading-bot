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
  initialBalance?: number;
  riskPerTradePct?: number;
  spreadPips?: number;
  commissionPerLot?: number;
  avgLots?: number;
};

export type BacktestTrade = {
  time?: string;
  entryTime?: string;
  exitTime?: string;
  direction?: string;
  entry?: number;
  sl?: number;
  tp?: number;
  tp1?: number;
  tp2?: number;
  lots?: number;
  riskAmount?: number;
  spreadPips?: number;
  commission?: number;
  outcome?: string;
  exit?: number;
  r_multiple?: number;
  pnl?: number;
  balance?: number;
};

export type BacktestReport = {
  id: string;
  symbol: string;
  timeframe: string;
  createdAt: string;
  source?: string;
  message?: string | null;
  bars?: number;
  strategy?: string;
  strategyLabel?: string;
  metrics: BacktestMetrics;
  trades: BacktestTrade[];
};

export type BacktestRequest = {
  symbol: string;
  timeframe: string;
  strategy?: string;
  useSample?: boolean;
  source?: string;
  sampleN?: number;
  initialBalance?: number;
  riskPerTradePct?: number;
  spreadPips?: number;
  commissionPerLot?: number;
  minLot?: number;
  maxLot?: number;
  partialClosePct?: number;
};
