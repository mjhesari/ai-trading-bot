# AI Trading Bot

Python **trading-engine** (SMC + real market APIs) + Next.js **dashboard**.

Works fully on **Mac** — no Windows. Deploy UI to **Vercel**, engine to a **Linux VPS**.

## Structure

```
ai-trading-bot/
├── trading-engine/   # FastAPI + Yahoo/Twelve Data + SMC
├── dashboard/        # Next.js → Vercel
├── docs/deploy.md    # Vercel + VPS steps
├── render.yaml       # optional Render blueprint
├── docker-compose.yml
└── .env.example
```

## Mac local (real Yahoo data)

```bash
cp .env.example .env

# Terminal 1 — engine
cd trading-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — UI
cd dashboard
cp .env.local.example .env.local
npm install
npm run dev
```

- UI: http://localhost:3000
- API docs: http://localhost:8000/docs

Default `DATA_SOURCE=yahoo` → charts, signals, and backtests all use **real FX OHLC**.

Optional second provider: set `TWELVE_DATA_API_KEY` in `.env` ([twelvedata.com](https://twelvedata.com)).

### Quick API checks

```bash
curl -s http://localhost:8000/api/health
curl -s "http://localhost:8000/api/market/EURUSD?timeframe=1h&source=yahoo&count=50"
curl -s "http://localhost:8000/api/signals?symbol=EURUSD&source=yahoo"
curl -s -X POST http://localhost:8000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{"symbol":"EURUSD","timeframe":"1h","source":"yahoo","sampleN":800}'
```

Look for `"source":"yahoo"` in responses.

## Deploy

See **[docs/deploy.md](docs/deploy.md)**.

| App               | Host                                                  |
| ----------------- | ----------------------------------------------------- |
| `dashboard/`      | Vercel (`NEXT_PUBLIC_ENGINE_URL=https://your-engine`) |
| `trading-engine/` | Render / Railway / Fly / any Linux VPS (Docker)       |

CORS already allows `https://*.vercel.app`.

## Tests

```bash
cd trading-engine
source .venv/bin/activate
pytest -q
```

## Disclaimer

Research tooling only — not financial advice.
