from fastapi import APIRouter
from app.core.config import Config as cfg
from app.api.routes.balance import coins_router, coins_ext_router
from app.api.routes.course import course_router
from app.api.routes.group import group_router
from app.api.routes.student import student_router
from app.api.routes.teacher import teacher_router
from app.api.routes.users import users_router
from app.api.routes.auth import auth_router
from app.api.routes.reward import shop_router

router = APIRouter()
router.include_router(course_router)
router.include_router(group_router)
router.include_router(student_router)
router.include_router(teacher_router)
router.include_router(users_router)
router.include_router(coins_router)
router.include_router(coins_ext_router)
router.include_router(auth_router)
router.include_router(shop_router)

@router.get("/")
async def root():
    return {"message": f"{cfg.PROJECT_NAME}: Hello World!"}
