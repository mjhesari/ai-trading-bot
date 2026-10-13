"""Mutable runtime market settings (editable from dashboard Settings)."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from app.core.config import get_settings
from app.market.session import DEFAULT_SESSION_TIMEZONE, resolve_timezone, session_snapshot

ALLOWED_SOURCES = ("yahoo", "twelvedata", "auto", "sample")


@dataclass
class RuntimeMarketConfig:
    data_source: str = "yahoo"
    twelve_data_api_key: str | None = None
    session_timezone: str = DEFAULT_SESSION_TIMEZONE


_lock = Lock()
_config: RuntimeMarketConfig | None = None


def _init_from_env() -> RuntimeMarketConfig:
    s = get_settings()
    tz = (s.session_timezone or DEFAULT_SESSION_TIMEZONE).strip() or DEFAULT_SESSION_TIMEZONE
    resolve_timezone(tz)
    return RuntimeMarketConfig(
        data_source=(s.data_source or "yahoo").lower(),
        twelve_data_api_key=s.twelve_data_api_key,
        session_timezone=tz,
    )


def get_runtime_config() -> RuntimeMarketConfig:
    global _config
    with _lock:
        if _config is None:
            _config = _init_from_env()
        return _config


def update_runtime_config(
    *,
    data_source: str | None = None,
    twelve_data_api_key: str | None = None,
    clear_twelve_key: bool = False,
    session_timezone: str | None = None,
) -> RuntimeMarketConfig:
    cfg = get_runtime_config()
    with _lock:
        if data_source is not None:
            mode = data_source.strip().lower()
            if mode not in ALLOWED_SOURCES:
                raise ValueError(f"Invalid data_source: {data_source}. Use one of {ALLOWED_SOURCES}")
            cfg.data_source = mode
        if session_timezone is not None:
            tz = session_timezone.strip() or DEFAULT_SESSION_TIMEZONE
            resolve_timezone(tz)
            cfg.session_timezone = tz
        if clear_twelve_key:
            cfg.twelve_data_api_key = None
        elif twelve_data_api_key is not None:
            key = twelve_data_api_key.strip()
            cfg.twelve_data_api_key = key or None
        return cfg


def public_settings_dict() -> dict:
    cfg = get_runtime_config()
    key = cfg.twelve_data_api_key
    masked = None
    if key:
        masked = f"{key[:4]}…{key[-4:]}" if len(key) > 8 else "****"
    snap = session_snapshot(cfg.session_timezone)
    return {
        "dataSource": cfg.data_source,
        "twelveDataApiKeySet": bool(key),
        "twelveDataApiKeyMasked": masked,
        "allowedSources": list(ALLOWED_SOURCES),
        "sessionTimezone": cfg.session_timezone,
        "sessionTimezoneLabel": snap["timezoneLabel"],
        "sessionOffset": snap["offset"],
        "allowedTimezones": snap["allowedTimezones"],
        "sessions": snap,
    }
