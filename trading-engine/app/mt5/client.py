"""Official MetaTrader5 client — real terminal connection (Windows/VPS)."""

from __future__ import annotations

import platform
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _import_mt5():
    try:
        import MetaTrader5 as mt5  # type: ignore

        return mt5
    except ImportError as exc:  # pragma: no cover - platform dependent
        raise RuntimeError(
            "MetaTrader5 package is not installed. "
            "Install on Windows/VPS: pip install MetaTrader5"
        ) from exc


class MT5Client:
    """Singleton-style connection manager around the official MetaTrader5 package."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.connected = False
        self.last_error: str | None = None
        self._mt5 = None

    @property
    def available(self) -> bool:
        if platform.system() != "Windows":
            return False
        try:
            _import_mt5()
            return True
        except RuntimeError:
            return False

    def connect(self) -> bool:
        self.last_error = None

        if platform.system() != "Windows":
            self.connected = False
            self.last_error = (
                f"Official MetaTrader5 Python API requires Windows "
                f"(current OS: {platform.system()}). "
                "Run trading-engine on a Windows VPS with MetaTrader 5 terminal installed."
            )
            logger.warning(self.last_error)
            return False

        try:
            mt5 = _import_mt5()
        except RuntimeError as exc:
            self.connected = False
            self.last_error = str(exc)
            logger.error(self.last_error)
            return False

        kwargs: dict[str, Any] = {}
        if self.settings.mt5_path:
            kwargs["path"] = self.settings.mt5_path
        if self.settings.mt5_login:
            kwargs["login"] = int(self.settings.mt5_login)
        if self.settings.mt5_password:
            kwargs["password"] = self.settings.mt5_password
        if self.settings.mt5_server:
            kwargs["server"] = self.settings.mt5_server

        if not mt5.initialize(**kwargs):
            err = mt5.last_error()
            self.connected = False
            self.last_error = f"MT5 initialize failed: {err}"
            logger.error(self.last_error)
            return False

        # Explicit login when credentials provided after initialize
        if self.settings.mt5_login and self.settings.mt5_password and self.settings.mt5_server:
            ok = mt5.login(
                login=int(self.settings.mt5_login),
                password=self.settings.mt5_password,
                server=self.settings.mt5_server,
            )
            if not ok:
                err = mt5.last_error()
                mt5.shutdown()
                self.connected = False
                self.last_error = f"MT5 login failed: {err}"
                logger.error(self.last_error)
                return False

        self._mt5 = mt5
        self.connected = True
        info = mt5.terminal_info()
        logger.info(
            "MT5 connected: terminal=%s company=%s",
            getattr(info, "name", "?"),
            getattr(info, "company", "?"),
        )
        return True

    def disconnect(self) -> None:
        if self._mt5 is not None:
            try:
                self._mt5.shutdown()
            except Exception:  # noqa: BLE001
                pass
        self._mt5 = None
        self.connected = False

    def api(self):
        if not self.connected or self._mt5 is None:
            raise RuntimeError(self.last_error or "MT5 is not connected")
        return self._mt5

    def ensure_symbol(self, symbol: str) -> str:
        mt5 = self.api()
        symbol = symbol.strip().upper().replace("/", "")
        info = mt5.symbol_info(symbol)
        if info is None:
            # Try common broker suffixes
            for suffix in ("", ".a", ".m", ".pro", ".raw", "m", "st"):
                candidate = f"{symbol}{suffix}" if suffix and not symbol.endswith(suffix) else symbol
                info = mt5.symbol_info(candidate)
                if info is not None:
                    symbol = candidate
                    break
        if info is None:
            raise ValueError(f"Symbol not found in MT5 Market Watch: {symbol}")
        if not info.visible:
            if not mt5.symbol_select(symbol, True):
                raise RuntimeError(f"Failed to select symbol {symbol} in Market Watch")
        return symbol

    def status(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "available": self.available,
            "connected": self.connected,
            "platform": platform.system(),
            "error": self.last_error,
            "login": self.settings.mt5_login,
            "server": self.settings.mt5_server,
            "path": self.settings.mt5_path,
        }
        if self.connected and self._mt5 is not None:
            ti = self._mt5.terminal_info()
            ai = self._mt5.account_info()
            payload["terminal"] = {
                "name": getattr(ti, "name", None),
                "company": getattr(ti, "company", None),
                "connected": getattr(ti, "connected", None),
                "tradeAllowed": getattr(ti, "trade_allowed", None),
            }
            if ai is not None:
                payload["account"] = {
                    "login": ai.login,
                    "name": ai.name,
                    "server": ai.server,
                    "currency": ai.currency,
                    "balance": ai.balance,
                    "equity": ai.equity,
                    "margin": ai.margin,
                    "leverage": ai.leverage,
                }
        return payload


_client: MT5Client | None = None


def get_mt5_client() -> MT5Client:
    global _client
    if _client is None:
        _client = MT5Client()
    return _client
