"""ML dataset builder — V1 unused."""

from __future__ import annotations

import pandas as pd


def build_dataset(candles: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    raise NotImplementedError("ML dataset building is not used in V1")
