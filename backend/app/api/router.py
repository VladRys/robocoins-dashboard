from fastapi import APIRouter
from core.config import Config as cfg

router = APIRouter()

@router.get("/")
async def root():
    return {"message": f"{cfg.PROJECT_NAME}: Hello World!"}
