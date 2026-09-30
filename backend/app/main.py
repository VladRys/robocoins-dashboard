from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.router import router
from core.config import Config as cfg
from core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await create_db_and_tables()
    yield


app = FastAPI(title=cfg.PROJECT_NAME, lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)