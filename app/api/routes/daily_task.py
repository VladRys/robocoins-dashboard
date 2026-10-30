from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_authenticated_user,
    get_authorization_service,
    get_daily_task_service,
)
from app.core.config import Config
from app.core.enums import AuthorizationAction, HttpErrorMessage, ProductMode
from app.models.user import User
from app.schemas.daily_task import (
    DailyTaskAnswer,
    DailyTaskAnswerResponse,
    DailyTaskResponse,
    DailyTaskTestAnswerResponse,
    DailyTaskTestResponse,
)
from app.services.daily_task import (
    DailyTaskAlreadyCompletedError,
    DailyTaskNotFoundError,
    DailyTaskService,
    StudentNotFoundError,
)
from app.services.authorization import AuthorizationService

daily_task_router = APIRouter(prefix="/daily", tags=["daily-tasks"])


def _require_test_mode() -> None:
    if Config.PRODUCT_MODE != ProductMode.DEV:
        raise HTTPException(status_code=404, detail="Not found")


@daily_task_router.get(
    "/{student_id}/daily-tasks",
    response_model=list[DailyTaskResponse],
)
async def get_daily_tasks(
    student_id: int,
    user: User = Depends(get_authenticated_user),
    service: DailyTaskService = Depends(get_daily_task_service),
    authorization: AuthorizationService = Depends(get_authorization_service),
):
    if not await authorization.is_allowed(
        AuthorizationAction.ACCESS_DAILY_TASK,
        user,
        student_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the student can access their daily task",
        )
    try:
        return await service.get_or_create_all(student_id)
    except StudentNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=HttpErrorMessage.STUDENT_NOT_FOUND,
        ) from error
    except DailyTaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="No daily tasks are available",
        ) from error


@daily_task_router.get(
    "/{student_id}/daily-task",
    response_model=DailyTaskResponse,
)
async def get_daily_task(
    student_id: int,
    user: User = Depends(get_authenticated_user),
    service: DailyTaskService = Depends(get_daily_task_service),
    authorization: AuthorizationService = Depends(get_authorization_service),
):
    if not await authorization.is_allowed(
        AuthorizationAction.ACCESS_DAILY_TASK,
        user,
        student_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the student can access their daily task",
        )
    try:
        return await service.get_or_create(student_id)
    except StudentNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=HttpErrorMessage.STUDENT_NOT_FOUND,
        ) from error
    except DailyTaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="No daily tasks are available",
        ) from error


@daily_task_router.get(
    "/{student_id}/dev-tasks",
    response_model=list[DailyTaskTestResponse],
)
async def get_daily_task_test_tasks(
    student_id: int,
    user: User = Depends(get_authenticated_user),
    service: DailyTaskService = Depends(get_daily_task_service),
    authorization: AuthorizationService = Depends(get_authorization_service),
):
    _require_test_mode()
    if not await authorization.is_allowed(
        AuthorizationAction.ACCESS_DAILY_TASK,
        user,
        student_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the student can access their daily task",
        )
    return await service.get_test_tasks()


@daily_task_router.post(
    "/{student_id}/dev-tasks/{task_id}/answer",
    response_model=DailyTaskTestAnswerResponse,
)
async def answer_daily_task_test_task(
    student_id: int,
    task_id: int,
    request: DailyTaskAnswer,
    user: User = Depends(get_authenticated_user),
    service: DailyTaskService = Depends(get_daily_task_service),
    authorization: AuthorizationService = Depends(get_authorization_service),
):
    _require_test_mode()
    if not await authorization.is_allowed(
        AuthorizationAction.ACCESS_DAILY_TASK,
        user,
        student_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the student can access their daily task",
        )
    try:
        return await service.answer_test_task(task_id, request.answer)
    except DailyTaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Daily task not found",
        ) from error


@daily_task_router.post(
    "/{student_id}/daily-task/answer",
    response_model=DailyTaskAnswerResponse,
)
async def answer_daily_task(
    student_id: int,
    request: DailyTaskAnswer,
    course_id: int | None = None,
    user: User = Depends(get_authenticated_user),
    service: DailyTaskService = Depends(get_daily_task_service),
    authorization: AuthorizationService = Depends(get_authorization_service),
):
    if not await authorization.is_allowed(
        AuthorizationAction.ACCESS_DAILY_TASK,
        user,
        student_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the student can access their daily task",
        )
    try:
        return await service.answer(
            student_id,
            request.answer,
            course_id=course_id,
        )
    except DailyTaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="No daily task is assigned for today",
        ) from error
    except DailyTaskAlreadyCompletedError as error:
        raise HTTPException(
            status_code=409,
            detail="Today's daily task is already completed",
        ) from error
    except StudentNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=HttpErrorMessage.STUDENT_NOT_FOUND,
        ) from error