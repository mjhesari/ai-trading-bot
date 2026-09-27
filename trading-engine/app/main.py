"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import backtest, health, market, mt5, signals
from app.api.routes import settings as settings_routes
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.runtime_config import get_runtime_config

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    runtime = get_runtime_config()
    logger.info(
        "trading-engine up · data_source=%s · twelvedata=%s · env=%s",
        runtime.data_source,
        bool(runtime.twelve_data_api_key),
        settings.app_env,
    )
    yield


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_origin_regex=settings.cors_origin_regex or None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(signals.router)
    app.include_router(market.router)
    app.include_router(backtest.router)
    app.include_router(settings_routes.router)
    app.include_router(mt5.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
