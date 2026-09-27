"""MT5 market data stub."""

from __future__ import annotations

import pandas as pd

from app.market.data import generate_sample_data


class MT5MarketData:
    def candles(self, symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
        # V1 fallback: sample data. Wire to MT5 copy_rates_from_pos later.
        _ = (symbol, timeframe)
        return generate_sample_data(n=count)
