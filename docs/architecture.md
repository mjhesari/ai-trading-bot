# Architecture

## Apps

1. **trading-engine** (Python / FastAPI) — Yahoo/Twelve Data OHLC, SMC, signals, backtest
2. **dashboard** (Next.js) — charts, signals, backtest UI → deploy on **Vercel**

## Data flow

```
Yahoo Finance (real) ──┐
Twelve Data (optional)─┼→ load_candles → SMC pipeline → Signals / Backtest
sample (fallback only)─┘
                              ↓
                     FastAPI → Next.js dashboard
```

Default `DATA_SOURCE=yahoo` on Mac, Linux, and VPS. No Windows dependency.

## Deploy

- Dashboard → Vercel
- Engine → Linux VPS / Render / Railway (see `docs/deploy.md`)

## Main API

- `GET /api/health`
- `GET /api/signals?source=yahoo`
- `GET /api/market/pairs`
- `GET /api/market/{symbol}?source=yahoo`
- `POST /api/backtest` body `{ "source": "yahoo", ... }`
