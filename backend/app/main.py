from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from api.router import router
from core.config import Config as cfg
from core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await create_db_and_tables()
    yield


app = FastAPI(title=cfg.PROJECT_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/registration", include_in_schema=False)
async def registration_page() -> FileResponse:
    page_path = Path(__file__).resolve().parents[2] / "frontend" / "register.html"
    return FileResponse(page_path, media_type="text/html")


if __name__ == "__main__":
    uvicorn.run(app, port=8000)