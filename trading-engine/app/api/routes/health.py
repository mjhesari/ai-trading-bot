"""Health check."""

from fastapi import APIRouter

from app.core.runtime_config import get_runtime_config, public_settings_dict
from app.market.provider import list_watchlist

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health() -> dict:
    runtime = get_runtime_config()
    return {
        "status": "ok",
        "service": "trading-engine",
        "dataSource": runtime.data_source,
        "providers": {
            "yahoo": True,
            "twelvedata": bool(runtime.twelve_data_api_key),
            "sample": True,
        },
        "settings": public_settings_dict(),
        "pairs": list_watchlist()[:8],
    }
