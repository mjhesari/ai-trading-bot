"""MT5 market orders — same connection used later for auto-trading."""

from __future__ import annotations

from typing import Any

from app.mt5.client import MT5Client, get_mt5_client


class MT5Orders:
    def __init__(self, client: MT5Client | None = None) -> None:
        self.client = client or get_mt5_client()

    def place(
        self,
        *,
        symbol: str,
        direction: str,
        volume: float,
        sl: float | None = None,
        tp: float | None = None,
        deviation: int = 20,
        comment: str = "aether-smc",
        magic: int = 260926,
    ) -> dict[str, Any]:
        if not self.client.connected:
            raise RuntimeError(self.client.last_error or "MT5 is not connected")

        mt5 = self.client.api()
        symbol = self.client.ensure_symbol(symbol)
        tick = mt5.symbol_info_tick(symbol)
        info = mt5.symbol_info(symbol)
        if tick is None or info is None:
            raise RuntimeError(f"Cannot quote {symbol}: {mt5.last_error()}")

        side = direction.upper()
        order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
        price = tick.ask if side == "BUY" else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "sl": float(sl or 0),
            "tp": float(tp or 0),
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None:
            raise RuntimeError(f"order_send returned None: {mt5.last_error()}")

        return {
            "retcode": result.retcode,
            "deal": result.deal,
            "order": result.order,
            "volume": result.volume,
            "price": result.price,
            "comment": result.comment,
            "requestId": result.request_id,
            "success": result.retcode == mt5.TRADE_RETCODE_DONE,
            "message": result.comment or str(result.retcode),
        }
