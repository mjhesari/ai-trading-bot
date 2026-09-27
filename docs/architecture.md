# Architecture (V1)

## Apps

Two independent applications, coordinated over HTTP:

1. **trading-engine** (Python / FastAPI) — market data, SMC, price action, strategy, risk, backtest, stubs for MT5/ML/execution
2. **dashboard** (Next.js) — signals list, backtest runner, placeholders for charts/settings

## Data flow

```
Sample/Yahoo → Market → SMC (swing/structure/liquidity/FVG/OB) → Price Action → SMCv1 → Signals → Risk
                                                                              ↘ Backtest
FastAPI exposes results → Next.js dashboard
```

## Boundaries

- FastAPI lives **inside** trading-engine (no third backend).
- MT5 terminal is **not** containerized; connect later from Windows/VPS.
- ML folders exist but are unused until rule-based edge is proven.
- Postgres schema is provisioned; V1 signals/backtests are in-memory.

## Main API

- `GET /api/health`
- `GET /api/signals`
- `GET /api/market/{symbol}`
- `POST /api/backtest`
- `GET /api/backtest/{id}`
