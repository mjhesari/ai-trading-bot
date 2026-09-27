#!/usr/bin/env bash
# Start Mac local stack: engine (Yahoo) + dashboard
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env from .env.example"
fi

cd "$ROOT/trading-engine"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

echo "Starting trading-engine on :8000 (DATA_SOURCE=yahoo)…"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
