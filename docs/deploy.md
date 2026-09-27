# Deploy

## Architecture

| Piece | Where | Why |
|-------|--------|-----|
| **dashboard** (Next.js) | **Vercel** | Static/SSR UI |
| **trading-engine** (FastAPI) | **VPS / Render / Railway / Fly** | Real Yahoo API, SMC, backtest — needs a real server |

Vercel cannot host the Python engine for this workload. Point the dashboard at the engine URL.

```
[Browser] → Vercel dashboard → NEXT_PUBLIC_ENGINE_URL → Engine on VPS
                                      ↓
                              Yahoo Finance (real OHLC)
```

---

## A) Local Mac (full real APIs)

```bash
# root
cp .env.example .env

# engine
cd trading-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# dashboard (other terminal)
cd dashboard
cp .env.local.example .env.local
npm install
npm run dev
```

- UI: http://localhost:3000  
- API: http://localhost:8000/docs  
- Default `DATA_SOURCE=yahoo` → real FX candles for charts / signals / backtests  

Optional: set `TWELVE_DATA_API_KEY` in `.env` for a second real provider.

---

## B) Dashboard → Vercel

1. Push repo to GitHub.
2. Vercel → New Project → root directory = `dashboard`.
3. Environment variable:

```
NEXT_PUBLIC_ENGINE_URL=https://YOUR-ENGINE-HOST
```

4. Deploy.

CORS on the engine already allows `https://*.vercel.app` via `CORS_ORIGIN_REGEX`.

Also set production CORS to your exact domain:

```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## C) Engine → Render (example)

1. Connect GitHub repo.
2. Use `render.yaml` or create a **Web Service**:
   - Root / Docker: `trading-engine/Dockerfile`
   - Health: `/api/health`
3. Env:

```
APP_ENV=production
DATA_SOURCE=yahoo
CORS_ORIGINS=https://your-app.vercel.app
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
TWELVE_DATA_API_KEY=   # optional
```

4. Copy the public URL into Vercel `NEXT_PUBLIC_ENGINE_URL`.

### Generic Linux VPS (Docker)

```bash
# on VPS
git clone <repo> && cd ai-trading-bot
cp .env.example .env
# edit CORS_ORIGINS to your Vercel URL
docker compose up -d --build trading-engine
```

Expose port `8000` (or put nginx + TLS in front).

---

## D) Verify real data

```bash
curl -s "https://YOUR-ENGINE/api/health"
curl -s "https://YOUR-ENGINE/api/market/EURUSD?timeframe=1h&source=yahoo&count=50"
curl -s "https://YOUR-ENGINE/api/signals?symbol=EURUSD&source=yahoo"
curl -s -X POST "https://YOUR-ENGINE/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"EURUSD","timeframe":"1h","source":"yahoo","sampleN":800}'
```

Each response includes `"source":"yahoo"` when live data is used.
