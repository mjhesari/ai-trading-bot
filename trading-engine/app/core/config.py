"""Application settings loaded from environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "trading-engine"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    default_symbol: str = "EURUSD"
    default_timeframe: str = "1h"
    lookback_period: str = "60d"
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

    mt5_login: int | None = None
    mt5_password: str | None = None
    mt5_server: str | None = None
    mt5_path: str | None = None

    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
