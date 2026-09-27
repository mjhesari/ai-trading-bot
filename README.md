# AI Trading Bot

Two coordinated apps: **Python trading engine** (SMC + price action) and **Next.js dashboard**.

## Structure

```
ai-trading-bot/
├── trading-engine/   # FastAPI + strategy + backtest
├── dashboard/        # Next.js UI
├── data/             # local datasets
├── docker/           # SQL init + docker helpers
├── docs/
├── docker-compose.yml
└── .env.example
```

## Quick start (local)

```bash
cp .env.example .env

# Engine
cd trading-engine
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Dashboard (other terminal)
cd dashboard
cp .env.local.example .env.local
npm install
npm run dev
```

- API: http://localhost:8000/docs  
- UI: http://localhost:3000  

## Docker

```bash
docker compose up --build
```

Postgres and Redis start with the stack. MT5 is intentionally outside Docker (Windows/VPS).

## V1 scope

- Working SMC V1 pipeline + signal model + backtest metrics
- FastAPI routes for health / signals / market / backtest
- Minimal dashboard pages for Signals and Backtest
- ML / live MT5 / WebSocket: stubs only

## Tests

```bash
cd trading-engine
pytest
```

## Disclaimer

Research tooling only — not financial advice. Validate on demo before any live trading.
