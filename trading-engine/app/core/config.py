"""Application settings loaded from environment."""

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _empty_as_none(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "trading-engine"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    default_symbol: str = "EURUSD"
    default_timeframe: str = "1h"
    lookback_period: str = "730d"
    # Primary real source on Mac / Linux / VPS. Options: yahoo | twelvedata | auto | sample
    data_source: str = "yahoo"
    forex_pairs: str = (
        "EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,USDCAD,NZDUSD,"
        "EURGBP,EURJPY,GBPJPY,AUDJPY,EURAUD,EURCHF,GBPCHF,XAUUSD"
    )

    # Optional second real API (https://twelvedata.com — free key)
    twelve_data_api_key: str | None = None

    swing_lookback: int = 5
    fvg_min_gap_pct: float = 0.0002
    liquidity_equal_tolerance: float = 0.0005
    premium_discount_level: float = 0.5
    risk_reward_ratio: float = 2.0
    sl_buffer_pct: float = 0.0005
    initial_balance: float = 10_000.0
    risk_per_trade_pct: float = 0.01

    database_url: str = "postgresql://trading:trading@localhost:5432/trading"
    redis_url: str = "redis://localhost:6379/0"

    # Optional / unused on Mac — kept only for future remote bridge
    mt5_auto_connect: bool = False
    mt5_login: int | None = None
    mt5_password: str | None = None
    mt5_server: str | None = None
    mt5_path: str | None = None

    cors_origins: str = "http://localhost:3000"
    cors_origin_regex: str = r"https://.*\.vercel\.app"

    @field_validator("mt5_login", mode="before")
    @classmethod
    def parse_mt5_login(cls, value: Any) -> Any:
        return _empty_as_none(value)

    @field_validator(
        "mt5_password",
        "mt5_server",
        "mt5_path",
        "twelve_data_api_key",
        mode="before",
    )
    @classmethod
    def parse_optional_strings(cls, value: Any) -> Any:
        return _empty_as_none(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
