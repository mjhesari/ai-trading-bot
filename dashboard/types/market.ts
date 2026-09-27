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
  count: number;
  candles: Candle[];
};
