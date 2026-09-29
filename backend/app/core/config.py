import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME: str = "RoboCoins Dashboard"
    PRODUCT_MODE: str = "DEV" # DEV, PROD 
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    