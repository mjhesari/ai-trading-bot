"""Named strategy registry used by signals + backtest APIs."""

from __future__ import annotations

from typing import Any, Callable

from app.strategy.strategies.ict_v1 import ICTv1Strategy
from app.strategy.strategies.smc_v1 import SMCv1Strategy

STRATEGIES: dict[str, dict[str, Any]] = {
    "smc": {
        "id": "smc",
        "label": "SMC v1",
        "description": "BOS / CHoCH + order block + FVG in premium/discount with PA trigger.",
        "factory": SMCv1Strategy,
    },
    "ict": {
        "id": "ict",
        "label": "ICT v1",
        "description": "Killzone + liquidity sweep + displacement/FVG. Entry, SL beyond sweep, TP at 2R / opposing liquidity.",
        "factory": ICTv1Strategy,
    },
}

DEFAULT_STRATEGY = "smc"


def list_strategies() -> list[dict[str, str]]:
    return [
        {
            "id": str(meta["id"]),
            "label": str(meta["label"]),
            "description": str(meta["description"]),
        }
        for meta in STRATEGIES.values()
    ]


def resolve_strategy(name: str | None, timeframe: str = "1h") -> tuple[str, Any]:
    key = (name or DEFAULT_STRATEGY).strip().lower()
    if key not in STRATEGIES:
        allowed = ", ".join(STRATEGIES)
        raise ValueError(f"Unknown strategy '{name}'. Use one of: {allowed}")
    meta = STRATEGIES[key]
    factory: Callable[..., Any] = meta["factory"]
    if key == "ict":
        return key, factory(timeframe=timeframe)
    return key, factory()
