from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.api.dependencies import (
    get_authenticated_user,
    get_authorization_service,
    get_daily_task_service,
)
from app.core.enums import AuthorizationAction, HttpErrorMessage
from app.models.user import User
from app.schemas.daily_task import (
    DailyTaskAnswer,
    DailyTaskAnswerResponse,
    DailyTaskResponse,
)
from app.services.daily_task import (
    DailyTaskAlreadyCompletedError,
    DailyTaskNotFoundError,
    DailyTaskService,
    StudentNotFoundError,
)
from app.services.authorization import AuthorizationService

daily_task_router = APIRouter(prefix="/student", tags=["daily-tasks"])

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


@daily_task_router.post(
    "/{student_id}/daily-task/answer",
    response_model=DailyTaskAnswerResponse,
)
async def answer_daily_task(
    student_id: int,
    request: DailyTaskAnswer,
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
        return await service.answer(student_id, request.answer)
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