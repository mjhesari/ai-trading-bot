"""MT5 account info."""

from __future__ import annotations

from typing import Any

from app.mt5.client import MT5Client, get_mt5_client


class MT5Account:
    def __init__(self, client: MT5Client | None = None) -> None:
        self.client = client or get_mt5_client()

    def info(self) -> dict[str, Any]:
        if not self.client.connected:
            return {
                "connected": False,
                "balance": None,
                "equity": None,
                "margin": None,
                "message": self.client.last_error or "MT5 not connected",
            }
        mt5 = self.client.api()
        ai = mt5.account_info()
        if ai is None:
            return {
                "connected": True,
                "balance": None,
                "equity": None,
                "margin": None,
                "message": f"account_info failed: {mt5.last_error()}",
            }
        return {
            "connected": True,
            "login": ai.login,
            "name": ai.name,
            "server": ai.server,
            "currency": ai.currency,
            "balance": ai.balance,
            "equity": ai.equity,
            "margin": ai.margin,
            "freeMargin": ai.margin_free,
            "leverage": ai.leverage,
            "profit": ai.profit,
            "message": "ok",
        }
