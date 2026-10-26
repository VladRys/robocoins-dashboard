from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.api.dependencies import (
    get_authenticated_admin,
    get_authenticated_user,
    get_authenticated_teacher,
    get_authorization_service,
    get_streak_service,
    get_student_service,
)
from app.api.errors import validation_error_message
from app.core.enums import AuthorizationAction, HttpErrorMessage, StatusEnum
from app.models.user import User
from app.schemas.student import (
    StudentAvatarEditRequest,
    StudentCreateRequest,
    StudentNicknameEditRequest,
    StudentProfileResponse,
    StudentResponse,
    BalanceLeaderboardEntry,
    BalanceLeaderboardResponse,
    BalanceLeaderboardRankResponse,
)
from app.schemas.auth import StudentCredentialsResponse
from app.services.authorization import AuthorizationService
from app.services.student import StudentService
from app.services.streak import StreakService
from app.schemas.streak import StreakResponse, LongestStreakResponse, StreakDaysUpdate

student_router = APIRouter(
    prefix="/student",
    tags=["students"],
)

@student_router.get("/{student_id}/streak", response_model=StreakResponse)
async def get_student_streak(student_id: int, streak_service: StreakService = Depends(get_streak_service)):
    return await streak_service.get_streak(student_id)

@student_router.get("/{student_id}/longest-streak", response_model=LongestStreakResponse)
async def get_student_longest_streak(student_id: int, streak_service: StreakService = Depends(get_streak_service)):
    return await streak_service.get_longest_streak(student_id)

@student_router.post("/{student_id}/streak/start", response_model=StreakResponse)
async def start_student_streak(student_id: int, streak_service: StreakService = Depends(get_streak_service)):
    return await streak_service.start_streak(student_id)

@student_router.post("/{student_id}/streak/end", response_model=StreakResponse)
async def end_student_streak(student_id: int, streak_service: StreakService = Depends(get_streak_service)):
    return await streak_service.end_streak(student_id)

@student_router.patch("/{student_id}/streak", response_model=StreakResponse)
async def update_student_streak(
    student_id: int,
    request: StreakDaysUpdate,
    streak_service: StreakService = Depends(get_streak_service),
    student_service: StudentService = Depends(get_student_service),
    _admin: User = Depends(get_authenticated_admin),
):
    if await student_service.get_student_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    streak = await streak_service.set_streak_days(student_id, request.days)
    if streak is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    return streak

@student_router.get("", response_model=list[StudentProfileResponse])
async def get_all_students(
    service: StudentService = Depends(get_student_service),
    _admin: User = Depends(get_authenticated_admin),
) -> list[StudentProfileResponse]:
    students = await service.get_all_students()
    return [StudentProfileResponse.model_validate(student) for student in students]


@student_router.get("/leaderboard/balance", response_model=BalanceLeaderboardResponse)
async def get_balance_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: StudentService = Depends(get_student_service),
    _user: User = Depends(get_authenticated_user),
) -> BalanceLeaderboardResponse:
    students, total = await service.get_balance_leaderboard(limit, offset)
    return BalanceLeaderboardResponse(
        entries=[
            BalanceLeaderboardEntry(
                rank=offset + index,
                student_id=student.id,
                name=student.name,
                avatar=student.avatar,
                course_names = [group.course.name for group in student.groups],
                balance=student.balance,
            )
            for index, student in enumerate(students, start=1)
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@student_router.get(
    "/leaderboard/balance/{student_id}",
    response_model=BalanceLeaderboardRankResponse,
)
async def get_balance_leaderboard_rank(
    student_id: int,
    service: StudentService = Depends(get_student_service),
    _user: User = Depends(get_authenticated_user),
) -> BalanceLeaderboardRankResponse:
    result = await service.get_balance_leaderboard_rank(student_id)
    if result is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    rank, student = result
    return BalanceLeaderboardRankResponse(
        student_id=student.id,
        rank=rank,
        balance=student.balance,
    )


@student_router.post("/register", response_model=StudentResponse)
async def create_student(
    student: StudentCreateRequest,
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    try:
        new_student = await service.create_student(student)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=validation_error_message(
                error,
                HttpErrorMessage.GROUPS_NOT_FOUND,
            ),
        ) from error

    if new_student is None:
        raise HTTPException(status_code=500, detail=HttpErrorMessage.FAILED_TO_CREATE_STUDENT)

    return StudentResponse(
        id=new_student.id,
        user_id=new_student.user_id,
        name=new_student.name,
        group_ids=[group.id for group in new_student.groups],
        course_names=list(dict.fromkeys(group.course.name for group in new_student.groups)),
        avatar=new_student.avatar,
        balance=new_student.balance,
        hash_access_key=new_student.hash_access_key,
        access_code=new_student.access_code,
        status=StatusEnum.SUCCESS,
        code=200,
    )


@student_router.get("/{student_id}", response_model=StudentProfileResponse)
async def get_student_by_id(
    student_id: int,
    service: StudentService = Depends(get_student_service),
    _user: User = Depends(get_authenticated_user),
) -> StudentProfileResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    return StudentProfileResponse.model_validate(student)

@student_router.patch("/{student_id}/avatar", response_model=StudentProfileResponse)
async def edit_student_avatar(
    student_id: int,
    request: StudentAvatarEditRequest,
    service: StudentService = Depends(get_student_service),
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> StudentProfileResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    can_edit_avatar = await authorization.is_allowed(
        AuthorizationAction.EDIT_STUDENT_AVATAR, user, student_id
    )
    if not can_edit_avatar:
        raise HTTPException(status_code=403, detail="You cannot change this student's avatar")

    updated_student = await service.update_avatar(student_id, request.new_avatar)
    if updated_student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    return StudentProfileResponse.model_validate(updated_student)

@student_router.patch("/{student_id}/access_code", response_model=StudentCredentialsResponse)
async def regenarate_student_access_code(student_id: int, service: StudentService = Depends(get_student_service), _user: User = Depends(get_authenticated_teacher), authorization: AuthorizationService = Depends(get_authorization_service)):
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    can_change_access_code = await authorization.is_allowed(AuthorizationAction.SHOW_STUDENT_CREDENTIALS, _user, student_id)
    if not can_change_access_code:
        raise HTTPException(status_code=403, detail=HttpErrorMessage.ONLY_GROUP_STUDENT_TEACHER_CAN_DO)

    updated_student = await service.update_student_access_code(student_id)
    if updated_student is None:
        raise HTTPException(status_code=500, detail=HttpErrorMessage.SOMETHING_WENT_WRONG)
    
    return StudentCredentialsResponse(
        user_id = updated_student.user_id,
        name = updated_student.name,
        access_code= updated_student.access_code
    )
    
@student_router.patch("/{student_id}/nickname", response_model=StudentProfileResponse)
async def edit_student_nickname(
    student_id: int,
    request: StudentNicknameEditRequest,
    service: StudentService = Depends(get_student_service),
    user: User = Depends(get_authenticated_user),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> StudentProfileResponse:
    student = await service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)

    can_edit_nickname = await authorization.is_allowed(
        AuthorizationAction.EDIT_STUDENT_NICKNAME,
        user,
        student_id,
    )
    if not can_edit_nickname:
        raise HTTPException(status_code=403, detail="You cannot change this student's nickname")

    updated_student = await service.update_nickname(student_id, request.new_nickname)
    if updated_student is None:
        raise HTTPException(status_code=404, detail=HttpErrorMessage.STUDENT_NOT_FOUND)
    return StudentProfileResponse.model_validate(updated_student)

@student_router.get("/{student_id}/credentials", response_model = StudentCredentialsResponse)
async def show_student_credentials(
    response: Response,
    student_id: int,
    _user: User = Depends(get_authenticated_teacher),
    student_service: StudentService = Depends(get_student_service),
    authorization: AuthorizationService = Depends(get_authorization_service)
) -> StudentCredentialsResponse:
    """Show student credentials for teacher (only if student in their group)"""
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    
    can_view_credentials = await authorization.is_allowed(
        AuthorizationAction.SHOW_STUDENT_CREDENTIALS,
        _user,
        student_id,
    )
    
    if not can_view_credentials:
        raise HTTPException(
            status_code=403,
            detail=HttpErrorMessage.ONLY_GROUP_STUDENT_TEACHER_CAN_DO
        )
        
    student = await student_service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=404,
            detail=HttpErrorMessage.STUDENT_NOT_FOUND,
        )
        
    return StudentCredentialsResponse(
        user_id = student.user_id,
        name = student.name,
        access_code= student.access_code
    )
