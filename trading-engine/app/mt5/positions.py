"""MT5 open positions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.mt5.client import MT5Client, get_mt5_client


class MT5Positions:
    def __init__(self, client: MT5Client | None = None) -> None:
        self.client = client or get_mt5_client()

    def list(self, symbol: str | None = None) -> list[dict[str, Any]]:
        if not self.client.connected:
            return []
        mt5 = self.client.api()
        positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
        if positions is None:
            return []
        out: list[dict[str, Any]] = []
        for p in positions:
            out.append(
                {
                    "ticket": p.ticket,
                    "symbol": p.symbol,
                    "type": "BUY" if p.type == 0 else "SELL",
                    "volume": p.volume,
                    "priceOpen": p.price_open,
                    "priceCurrent": p.price_current,
                    "sl": p.sl,
                    "tp": p.tp,
                    "profit": p.profit,
                    "swap": p.swap,
                    "time": datetime.fromtimestamp(p.time, tz=timezone.utc).isoformat(),
                    "comment": p.comment,
                }
            )
        return out
