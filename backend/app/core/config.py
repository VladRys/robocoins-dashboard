import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME: str = "RoboCoins Dashboard"
    PRODUCT_MODE: str = os.getenv("PRODUCT_MODE", "DEV").upper()
    DEV_DATABASE_URL: str = os.getenv(
        "DEV_DATABASE_URL", "sqlite+aiosqlite:///./dev.db"
    )
    PROD_DATABASE_URL: str | None = os.getenv("PROD_DATABASE_URL") or os.getenv(
        "DATABASE_URL"
    )

    if PRODUCT_MODE == "DEV":
        DATABASE_URL: str = DEV_DATABASE_URL
    elif PRODUCT_MODE == "PROD":
        if not PROD_DATABASE_URL:
            raise ValueError(
                "Set PROD_DATABASE_URL or DATABASE_URL when PRODUCT_MODE=PROD"
            )
        DATABASE_URL = PROD_DATABASE_URL
    else:
        raise ValueError("PRODUCT_MODE must be either DEV or PROD")
