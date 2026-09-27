"""MT5 client stub — real terminal lives on Windows/VPS, not Mac Docker."""

from __future__ import annotations

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MT5Client:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.connected = False

    def connect(self) -> bool:
        if not self.settings.mt5_login:
            logger.warning("MT5 credentials not configured; client remains disconnected")
            self.connected = False
            return False
        # Real MetaTrader5 package is Windows-only; stub for V1.
        raise NotImplementedError(
            "MT5 live connection is not available in this environment. "
            "Run the official MetaTrader5 Python package on Windows/VPS."
        )

    def disconnect(self) -> None:
        self.connected = False
