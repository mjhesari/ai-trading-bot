-- PostgreSQL schema skeleton for V1 (engine still uses in-memory for signals/backtests)

CREATE TABLE IF NOT EXISTS symbols (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  broker_symbol TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS candles (
  id BIGSERIAL PRIMARY KEY,
  symbol_id INT REFERENCES symbols(id),
  timeframe TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  open DOUBLE PRECISION NOT NULL,
  high DOUBLE PRECISION NOT NULL,
  low DOUBLE PRECISION NOT NULL,
  close DOUBLE PRECISION NOT NULL,
  volume DOUBLE PRECISION,
  UNIQUE (symbol_id, timeframe, ts)
);

CREATE TABLE IF NOT EXISTS market_sessions (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  start_hour INT,
  end_hour INT
);

CREATE TABLE IF NOT EXISTS strategies (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  version TEXT NOT NULL,
  config JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS strategy_runs (
  id UUID PRIMARY KEY,
  strategy_id INT REFERENCES strategies(id),
  started_at TIMESTAMPTZ DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  status TEXT
);

CREATE TABLE IF NOT EXISTS signals (
  id UUID PRIMARY KEY,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  direction TEXT NOT NULL,
  entry DOUBLE PRECISION,
  stop_loss DOUBLE PRECISION,
  take_profit_1 DOUBLE PRECISION,
  take_profit_2 DOUBLE PRECISION,
  risk_reward DOUBLE PRECISION,
  confidence DOUBLE PRECISION,
  reasons JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signal_events (
  id BIGSERIAL PRIMARY KEY,
  signal_id UUID REFERENCES signals(id),
  event_type TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades (
  id UUID PRIMARY KEY,
  signal_id UUID REFERENCES signals(id),
  mode TEXT,
  status TEXT,
  opened_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS positions (
  id UUID PRIMARY KEY,
  symbol TEXT NOT NULL,
  direction TEXT NOT NULL,
  volume DOUBLE PRECISION,
  entry DOUBLE PRECISION,
  stop_loss DOUBLE PRECISION,
  take_profit DOUBLE PRECISION,
  opened_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS backtests (
  id UUID PRIMARY KEY,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metrics JSONB
);

CREATE TABLE IF NOT EXISTS backtest_trades (
  id BIGSERIAL PRIMARY KEY,
  backtest_id UUID REFERENCES backtests(id),
  payload JSONB
);

CREATE TABLE IF NOT EXISTS backtest_metrics (
  backtest_id UUID PRIMARY KEY REFERENCES backtests(id),
  metrics JSONB
);

CREATE TABLE IF NOT EXISTS model_versions (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_predictions (
  id BIGSERIAL PRIMARY KEY,
  model_version_id INT REFERENCES model_versions(id),
  signal_id UUID,
  probability DOUBLE PRECISION,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
