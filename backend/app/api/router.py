from fastapi import APIRouter
from core.config import Config as cfg
from api.routes.balance import coins_router
from api.routes.course import course_router
from api.routes.group import group_router
from api.routes.student import student_router

router = APIRouter()
router.include_router(course_router)
router.include_router(group_router)
router.include_router(student_router)
router.include_router(coins_router)

@router.get("/")
async def root():
    return {"message": f"{cfg.PROJECT_NAME}: Hello World!"}
