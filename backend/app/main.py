import uvicorn
from fastapi import FastAPI

from api.router import router
from core.config import Config as cfg

app = FastAPI(title=cfg.PROJECT_NAME)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)