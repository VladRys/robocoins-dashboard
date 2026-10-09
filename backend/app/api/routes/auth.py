from fastapi import Depends, HTTPException, APIRouter, Request, Response
from schemas.auth import StudentLogin, StudentLoginResponse
from services.student import StudentService, get_student_service
from services.session import SessionService, get_session_service


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/login", response_model=StudentLoginResponse)
async def login(login_request: StudentLogin, response: Response, request: Request, student_service: StudentService = Depends(get_student_service), session_service: SessionService = Depends(get_session_service)):
    student = await student_service.get_student_by_access_code(login_request.code)

    if not student:
        raise HTTPException(status_code=404, detail="Wrong access code")

    session = await session_service.create_session(student.id)
    session_token = session.token_hash

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age = 60 * 60 * 24 * 7  # 1 week
        )

    return StudentLoginResponse(
        message="Login successful",
        session_token=session_token,
        )

@auth_router.post("/logout")
async def logout(request: Request, response: Response, session_service: SessionService = Depends(get_session_service)):
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await session_service.delete_session(token)
    response.delete_cookie("session_token")

@auth_router.get("/me", response_model=StudentLoginResponse)
async def get_current_student(request: Request, student_service: StudentService = Depends(get_student_service), session_service: SessionService = Depends(get_session_service)):
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = await session_service.get_session_by_token(token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session token")

    student = await student_service.get_student_by_id(session.student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return StudentLoginResponse(
        message="Current student retrieved successfully",
        session_token=token,
        )
