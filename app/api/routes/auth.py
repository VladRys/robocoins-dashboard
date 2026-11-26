import hmac
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.api.dependencies import (
    get_authenticated_user,
    get_authorization_service,
    get_google_oauth_service,
    get_session_service,
    get_student_service,
    get_user_service,
)
from app.core.config import Config as cfg
from app.core.enums import (
    AuthorizationAction,
    GoogleOAuthFlow,
    GoogleOAuthStatus,
    HttpErrorMessage,
    UserRole,
)
from app.models.user import User
from app.repositories.users import GoogleAccountAlreadyLinkedError
from app.schemas.auth import (
    AdminProfileResponse,
    GoogleAuthorizationResponse,
    GoogleLinkStatusResponse,
    GoogleOAuthCallbackResponse,
    GoogleOAuthStatusesResponse,
    StudentCredentialsResponse,
    UserLogoutResponse,
    UserLoginRequest,
    UserLoginResponse,
)
from app.schemas.student import StudentProfileResponse
from app.schemas.teacher import TeacherGroupProfile, TeacherProfileResponse
from app.services.authorization import AuthorizationService
from app.services.session import SessionService
from app.services.google_oauth import GoogleOAuthError, GoogleOAuthService
from app.services.student import StudentService
from app.services.users import UserService


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def _set_session_cookie(
    response: Response,
    request: Request,
    session_token: str,
) -> None:
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )


def _set_google_state_cookie(
    response: Response,
    request: Request,
    state: str,
) -> None:
    response.set_cookie(
        key="google_oauth_state",
        value=state,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 10,
        path="/",
    )


def _google_result_response(
    response: Response,
    result: GoogleOAuthStatus,
) -> GoogleOAuthCallbackResponse:
    response.headers["Cache-Control"] = "no-store"
    response.delete_cookie("google_oauth_state", path="/")
    return GoogleOAuthCallbackResponse(status=result)


@auth_router.get(
    "/google/login",
    response_model=GoogleAuthorizationResponse,
    include_in_schema=False,
)
async def start_google_login(
    response: Response,
    request: Request,
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
) -> GoogleAuthorizationResponse:
    try:
        authorization = await google_oauth.create_authorization_url(GoogleOAuthFlow.LOGIN)
    except GoogleOAuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    response.headers["Cache-Control"] = "no-store"
    _set_google_state_cookie(response, request, authorization.state)
    return GoogleAuthorizationResponse(authorization_url=authorization.url)


@auth_router.post("/google/link", response_model=GoogleAuthorizationResponse)
async def start_google_link(
    response: Response,
    request: Request,
    user: User = Depends(get_authenticated_user),
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
) -> GoogleAuthorizationResponse:
    try:
        authorization = await google_oauth.create_authorization_url(
            GoogleOAuthFlow.LINK,
            user_id=user.id,
        )
    except GoogleOAuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    response.headers["Cache-Control"] = "no-store"
    _set_google_state_cookie(response, request, authorization.state)
    return GoogleAuthorizationResponse(authorization_url=authorization.url)


@auth_router.get("/google/status", response_model=GoogleLinkStatusResponse)
async def get_google_link_status(
    response: Response,
    user: User = Depends(get_authenticated_user),
) -> GoogleLinkStatusResponse:
    response.headers["Cache-Control"] = "no-store"
    return GoogleLinkStatusResponse(
        linked=user.google_sub is not None,
        email=user.google_email,
    )


@auth_router.delete("/google/link", response_model=GoogleLinkStatusResponse)
async def remove_google_link(
    user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
) -> GoogleLinkStatusResponse:
    updated_user = await user_service.unlink_google_account(user.id)
    return GoogleLinkStatusResponse(linked=False, email=updated_user.google_email)


@auth_router.get(
    "/google/statuses",
    response_model=GoogleOAuthStatusesResponse,
)
async def get_google_oauth_statuses() -> GoogleOAuthStatusesResponse:
    return GoogleOAuthStatusesResponse(statuses=list(GoogleOAuthStatus))


@auth_router.get(
    "/google/callback",
    response_model=GoogleOAuthCallbackResponse,
    include_in_schema=False,
)
async def google_oauth_callback(
    response: Response,
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
    user_service: UserService = Depends(get_user_service),
    student_service: StudentService = Depends(get_student_service),
    session_service: SessionService = Depends(get_session_service),
) -> GoogleOAuthCallbackResponse:
    state_cookie = request.cookies.get("google_oauth_state")
    if (
        not state
        or not state_cookie
        or len(state) > 128
        or not state.isascii()
        or not state_cookie.isascii()
        or not hmac.compare_digest(state, state_cookie)
    ):
        return _google_result_response(response, GoogleOAuthStatus.INVALID_STATE)

    pending = await google_oauth.consume_state(state)
    if pending is None:
        return _google_result_response(response, GoogleOAuthStatus.INVALID_STATE)
    if error is not None:
        return _google_result_response(response, GoogleOAuthStatus.CANCELLED)
    if not code:
        return _google_result_response(response, GoogleOAuthStatus.VERIFICATION_FAILED)

    try:
        identity = await google_oauth.exchange_code(
            code,
            pending.code_verifier,
            pending.nonce,
        )
    except GoogleOAuthError:
        return _google_result_response(response, GoogleOAuthStatus.VERIFICATION_FAILED)

    if pending.flow == GoogleOAuthFlow.LINK and pending.user_id is not None:
        token = request.cookies.get("session_token")
        session = (
            await session_service.get_session_by_token(token)
            if token is not None
            else None
        )
        if (
            session is None
            or session.is_expired()
            or session.user_id != pending.user_id
        ):
            return _google_result_response(response, GoogleOAuthStatus.SESSION_EXPIRED)
        try:
            await user_service.link_google_account(
                pending.user_id,
                identity.sub,
                identity.email,
            )
        except GoogleAccountAlreadyLinkedError:
            return _google_result_response(response, GoogleOAuthStatus.ALREADY_LINKED)
        return _google_result_response(response, GoogleOAuthStatus.LINKED)

    if pending.flow != GoogleOAuthFlow.LOGIN or pending.user_id is not None:
        return _google_result_response(response, GoogleOAuthStatus.INVALID_STATE)

    user = await user_service.get_user_by_google_sub(identity.sub)
    if user is None:
        return _google_result_response(response, GoogleOAuthStatus.NOT_LINKED)
    if user.role == UserRole.STUDENT.value:
        student = await student_service.get_student_by_id(user.id)
        if student is None:
            return _google_result_response(response, GoogleOAuthStatus.PROFILE_MISSING)

    student_id = user.id if user.role == UserRole.STUDENT.value else None
    session_token = await session_service.create_session(user.id, student_id)
    response.headers["Cache-Control"] = "no-store"
    response.delete_cookie("google_oauth_state", path="/")
    result = GoogleOAuthCallbackResponse(
        status=GoogleOAuthStatus.LOGIN,
        user={"id": user.id, "user_id": user.id, "name": user.name, "role": user.role},
    )
    _set_session_cookie(response, request, session_token)
    return result

@auth_router.get("/me/credentials", response_model=StudentCredentialsResponse)
async def get_student_credentials(
    response: Response,
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
    student_service: StudentService = Depends(get_student_service),
) -> StudentCredentialsResponse:
    """Students can view only their own credentials"""
    
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    can_view_credentials = await authorization.is_allowed(
        AuthorizationAction.VIEW_STUDENT_CREDENTIALS,
        user,
        user.id,
    )
    if not can_view_credentials:
        raise HTTPException(
            status_code=403,
            detail=HttpErrorMessage.ONLY_STUDENTS_CAN_VIEW_CREDENTIALS,
        )

    student = await student_service.get_student_by_id(user.id)
    if student is None:
        raise HTTPException(
            status_code=404,
            detail=HttpErrorMessage.STUDENT_NOT_FOUND,
        )

    return StudentCredentialsResponse(
        user_id=student.user_id,
        name=student.name,
        access_code=student.access_code,
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
    if len(login_request.code) == 12:
        configured_password = cfg.ADMIN_PASSWORD
        if not configured_password or not hmac.compare_digest(
            login_request.code.encode("utf-8"), configured_password.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Invalid login credentials")

        user = await user_service.get_or_create_admin_user()
        session_token = await session_service.create_session(user.id)
        _set_session_cookie(response, request, session_token)
        response.headers["Cache-Control"] = "no-store"
        return UserLoginResponse(
            message="Login successful",
            session_token=session_token,
            user={"id": user.id, "user_id": user.id, "name": user.name, "role": user.role},
        )

    user = await user_service.get_user_by_access_code(login_request.code)
    if user is None:
        raise HTTPException(status_code=401, detail=HttpErrorMessage.WRONG_ACCESS_CODE)

    student_id = user.id if user.role == UserRole.STUDENT.value else None
    if student_id is not None:
        student = await student_service.get_student_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_PROFILE_NOT_FOUND)

    session_token = await session_service.create_session(user.id, student_id)

    _set_session_cookie(response, request, session_token)
    response.headers["Cache-Control"] = "no-store"

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
    response_model=StudentProfileResponse | TeacherProfileResponse | AdminProfileResponse,
)
async def get_current_user(
    request: Request,
    student_service: StudentService = Depends(get_student_service),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> StudentProfileResponse | TeacherProfileResponse | AdminProfileResponse:
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
            current_goal=getattr(student, "current_goal", None),
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

    if user.role == UserRole.ADMIN.value:
        return AdminProfileResponse(
            id=user.id,
            user_id=user.id,
            name=user.name,
            role=UserRole.ADMIN,
        )

    raise HTTPException(status_code=403, detail=HttpErrorMessage.UNSUPPORTED_USER_ROLE)
