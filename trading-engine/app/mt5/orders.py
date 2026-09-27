"""MT5 orders stub."""

from __future__ import annotations

from typing import Any


class MT5Orders:
    def place(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Live order placement requires MT5 on Windows/VPS")
