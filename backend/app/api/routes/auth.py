from fastapi import Depends, HTTPException, APIRouter, Response
from schemas.auth import StudentLogin, StudentLoginResponse
from schemas.student import StudentResponse
from sqlalchemy.orm import AsyncSession
from core.database import get_db
from services.student import StudentService, get_student_service
from service.auth import AuthService, get_auth_service
from services.session import SessionService, get_session_service


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/login", response_model=StudentLoginResponse)
async def login(request: StudentLogin, response: Response, db: AsyncSession = Depends(get_db), student_service: StudentService = Depends(get_student_service), session_service: SessionService = Depends(get_session_service)):
    student = await student_service.get_student_by_access_code(request.access_code)

    if not student:
        raise HTTPException(status_code=404, detail="Wrong access code")

    session_token = session_service.create_session(student.id)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age = 60 * 60 * 24 * 7  # 1 week
        )

    return StudentLoginResponse(
        message="Login successful",
        session_token=session_token,
        )

@auth_router.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_db), auth_service: AuthService = Depends(get_auth_service)):
    token = response.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await auth_service.session_service.delete_session(token)

@auth_router.get("/me")
async def get_current_student(response: Response, db: AsyncSession = Depends(get_db), auth_service: AuthService = Depends(get_auth_service)):
    token = response.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    student = await auth_service.get_current_student(token)
    return StudentResponse(
        id=student.id,
        name=student.name,
        avatar=student.avatar,
        balance=student.balance,
        course_name=student.course_name,
        group_id=student.group_id,
        hash_access_key=student.hash_access_key,
        access_code=student.access_code
        )


