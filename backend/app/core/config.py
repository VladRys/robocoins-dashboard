import os
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from urllib.parse import urlsplit

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
    origins: list[str] = []
    for configured_origin in os.getenv("PROD_CORS_ORIGINS", "").split(","):
        configured_origin = configured_origin.strip().rstrip("/")
        if not configured_origin:
            continue
        if "://" not in configured_origin:
            parsed_host = urlsplit(f"http://{configured_origin}").hostname
            scheme = (
                "http"
                if parsed_host in {"localhost", "127.0.0.1", "::1"}
                else "https"
            )
            configured_origin = f"{scheme}://{configured_origin}"

        parsed_origin = urlsplit(configured_origin)
        if (
            parsed_origin.scheme not in {"http", "https"}
            or parsed_origin.hostname is None
            or parsed_origin.path
            or parsed_origin.query
            or parsed_origin.fragment
            or parsed_origin.username is not None
            or parsed_origin.password is not None
        ):
            raise ValueError(
                f"Invalid origin in PROD_CORS_ORIGINS: {configured_origin!r}"
            )
        origins.append(
            f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        )
    return origins


LOCAL_CORS_ORIGIN_REGEX = (
    r"^https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$"
)


CORS_ORIGINS_BY_MODE = {
    ProductMode.DEV: [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    ProductMode.PROD: prod_cors_origins(),
}

class Config:
    PROJECT_NAME = "RoboCoins Dashboard"
    PRODUCT_MODE, DATABASE_URL = resolve_database_url(
        os.getenv("PRODUCT_MODE", ProductMode.DEV.value)
    )
    CORS_ORIGINS = CORS_ORIGINS_BY_MODE[PRODUCT_MODE]
    CORS_ORIGIN_REGEX = LOCAL_CORS_ORIGIN_REGEX
