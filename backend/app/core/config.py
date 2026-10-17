import os
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv

from core.enums import ProductMode

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def dev_database_url() -> str:
    return os.getenv("DEV_DATABASE_URL", "sqlite+aiosqlite:///./dev.db")

def prod_database_url() -> str:
    url = os.getenv("PROD_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("Set PROD_DATABASE_URL or DATABASE_URL when PRODUCT_MODE=PROD")
    return url


DATABASE_URL_RESOLVERS: dict[ProductMode, Callable[[], str]] = {
    ProductMode.DEV: dev_database_url,
    ProductMode.PROD: prod_database_url,
}

def resolve_database_url(raw_mode: str) -> tuple[ProductMode, str]:
    try:
        mode = ProductMode(raw_mode.upper())
    except ValueError as exc:
        allowed = ", ".join(mode.value for mode in ProductMode)
        raise ValueError(f"PRODUCT_MODE must be one of: {allowed}") from exc

    return mode, DATABASE_URL_RESOLVERS[mode]()

def prod_cors_origins() -> list[str]:
    try:
        origins = [origin.strip() for origin in os.getenv("PROD_CORS_ORIGINS", "").split(",") if origin.strip()]
    except ValueError:
        raise ValueError("set PROD_CORS_ORIGINS first.")
    
    return origins
    
CORS_ORIGINS_BY_MODE = {
    ProductMode.DEV: ["http://localhost:5500","http://127.0.0.1:5500"],
    ProductMode.PROD: prod_cors_origins(),
}

class Config:
    PROJECT_NAME = "RoboCoins Dashboard"
    PRODUCT_MODE, DATABASE_URL = resolve_database_url(
        os.getenv("PRODUCT_MODE", ProductMode.DEV.value)
    )
    CORS_ORIGINS = CORS_ORIGINS_BY_MODE[PRODUCT_MODE]
