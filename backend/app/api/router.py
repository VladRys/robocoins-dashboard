from fastapi import APIRouter
from core.config import Config as cfg
from api.routes.student import student_router

router = APIRouter()
router.include_router(student_router)

@router.get("/")
async def root():
    return {"message": f"{cfg.PROJECT_NAME}: Hello World!"}
