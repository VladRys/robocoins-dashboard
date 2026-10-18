from fastapi import Depends, HTTPException, APIRouter, Request, Response
from app.core.enums import HttpErrorMessage, UserRole
from schemas.student import StudentProfileResponse
from schemas.teacher import TeacherGroupProfile, TeacherProfileResponse
from schemas.auth import (
    UserLogoutResponse,
    UserLoginRequest,
    UserLoginResponse,
)
from services.student import StudentService, get_student_service
from services.session import SessionService, get_session_service
from services.users import UserService, get_user_service


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/login", response_model=UserLoginResponse)
async def login(
    login_request: UserLoginRequest,
    response: Response,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    student_service: StudentService = Depends(get_student_service),
    session_service: SessionService = Depends(get_session_service),
) -> UserLoginResponse:
    user = await user_service.get_user_by_access_code(login_request.code)
    if user is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.WRONG_ACCESS_CODE)

    student_id = user.id if user.role == UserRole.STUDENT.value else None
    if student_id is not None:
        student = await student_service.get_student_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_PROFILE_NOT_FOUND)

    session_token = await session_service.create_session(user.id, student_id)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age = 60 * 60 * 24 * 7  # 1 week
        )

    return UserLoginResponse(
        message="Login successful",
        session_token=session_token,
        user={
            "id": user.id,
            "user_id": user.id,
            "name": user.name,
            "role": user.role,
        },
    )

@auth_router.post("/logout", response_model=UserLogoutResponse)
async def logout(request: Request, response: Response, session_service: SessionService = Depends(get_session_service)):
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.NOT_AUTHENTICATED)

    await session_service.delete_session(token)
    response.delete_cookie("session_token")

    return UserLogoutResponse(
        message="Logout successful"
    )

@auth_router.get(
    "/me",
    response_model=StudentProfileResponse | TeacherProfileResponse,
)
async def get_current_user(
    request: Request,
    student_service: StudentService = Depends(get_student_service),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> StudentProfileResponse | TeacherProfileResponse:
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.NOT_AUTHENTICATED)

    session = await session_service.get_session_by_token(token)

    if not session:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.INVALID_SESSION_TOKEN)

    if session.is_expired():
        await session_service.delete_session(token)
        raise HTTPException(status_code=401, detail=HttpErrorMessage.SESSION_EXPIRED)
    
    user = await user_service.get_user_by_id(session.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.USER_NOT_FOUND)

    if user.role == UserRole.STUDENT.value:
        student = await student_service.get_student_by_id(user.id)
        if student is None:
            raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

        return StudentProfileResponse(
            id=student.id,
            user_id=student.user_id,
            name=student.name,
            group_ids=[group.id for group in student.groups],
            course_names=list(dict.fromkeys(group.course.name for group in student.groups)),
            avatar=student.avatar,
            balance=student.balance,
        )

    if user.role == UserRole.TEACHER.value:
        profile = await user_service.get_teacher_profile(user.id)
        if profile is None:
            raise HTTPException(status_code=404, detail=HttpErrorMessage.TEACHER_PROFILE_NOT_FOUND)
        teacher, groups = profile
        return TeacherProfileResponse(
            id=teacher.id,
            user_id=teacher.id,
            name=teacher.name,
            role=UserRole.TEACHER,
            groups=[
                TeacherGroupProfile(
                    id=group.id,
                    name=group.name,
                    course_id=group.course_id,
                    course_name=group.course.name,
                    students_count=len(group.students),
                )
                for group in groups
            ],
        )

    raise HTTPException(status_code=403, detail=HttpErrorMessage.UNSUPPORTED_USER_ROLE)
