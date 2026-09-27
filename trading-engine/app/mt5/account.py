"""MT5 account stub."""

from __future__ import annotations

from typing import Any


class MT5Account:
    def info(self) -> dict[str, Any]:
        return {
            "connected": False,
            "balance": None,
            "equity": None,
            "margin": None,
            "message": "MT5 account unavailable in V1 stub",
        }
