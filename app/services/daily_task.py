from datetime import date, datetime, timezone

from sqlalchemy import case, select, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import BalanceChangeReasons
from app.models.daily_task import DailyTask, DailyTaskQuestion, StudentDailyTask
from app.models.group import Group
from app.models.student import Student
from app.models.transaction import BalanceTransaction
from app.schemas.daily_task import DailyTaskAnswerResponse, DailyTaskResponse


class DailyTaskNotFoundError(Exception):
    pass


class DailyTaskAlreadyCompletedError(Exception):
    pass


class StudentNotFoundError(Exception):
    pass


class DailyTaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, student_id: int) -> DailyTaskResponse:
        today = date.today()
        assignment = await self._get_assignment(student_id, today)
        if assignment is not None:
            return self._response(assignment)

        student = await self.session.scalar(
            select(Student)
            .options(selectinload(Student.groups).selectinload(Group.course))
            .where(Student.id == student_id)
            .with_for_update()
        )
        if student is None:
            raise StudentNotFoundError

        assignment = await self._get_assignment(student_id, today)
        if assignment is not None:
            return self._response(assignment)

        course_categories = {
            group.course.category.value for group in student.groups
        }
        available_tasks = list(
            (
                await self.session.scalars(
                    select(DailyTask)
                    .options(joinedload(DailyTask.question))
                    .order_by(
                        case((DailyTask.last_date.is_(None), 0), else_=1),
                        DailyTask.last_date.asc(),
                        DailyTask.id.asc(),
                    )
                )
            ).all()
        )
        task = next(
            (
                candidate
                for candidate in available_tasks
                if not candidate.question.course_categories
                or course_categories.intersection(
                    candidate.question.course_categories
                )
            ),
            None,
        )
        if task is None:
            raise DailyTaskNotFoundError

        task.last_date = today
        assignment = StudentDailyTask(
            student_id=student_id,
            daily_task=task,
            task_date=today,
        )
        self.session.add(assignment)
        await self.session.commit()
        await self.session.refresh(assignment)
        return self._response(assignment)

    async def answer(
        self,
        student_id: int,
        answer: str,
    ) -> DailyTaskAnswerResponse:
        assignment = await self._get_assignment(student_id, date.today(), lock=True)
        if assignment is None:
            raise DailyTaskNotFoundError
        if assignment.completed_at is not None:
            raise DailyTaskAlreadyCompletedError

        question = assignment.daily_task.question
        is_correct = answer.strip().casefold() == question.answer.strip().casefold()
        completed_at = datetime.now(timezone.utc)
        assignment.submitted_answer = answer.strip()
        assignment.correct = is_correct
        assignment.completed_at = completed_at

        if is_correct:
            balance = await self.session.scalar(
                update(Student)
                .where(Student.id == student_id)
                .values(balance=Student.balance + question.reward)
                .returning(Student.balance)
            )
            if balance is None:
                raise StudentNotFoundError
            self.session.add(
                BalanceTransaction(
                    student_id=student_id,
                    operation="deposit",
                    amount=question.reward,
                    reason=[BalanceChangeReasons.ADDITIONAL_TASK_COMPLETED.value],
                )
            )
        else:
            student = await self.session.get(Student, student_id)
            if student is None:
                raise StudentNotFoundError
            balance = student.balance

        await self.session.commit()
        return DailyTaskAnswerResponse(
            correct=is_correct,
            completed_at=completed_at,
            reward=question.reward if is_correct else 0.0,
            balance=balance,
        )

    async def _get_assignment(
        self,
        student_id: int,
        task_date: date,
        *,
        lock: bool = False,
    ) -> StudentDailyTask | None:
        statement = (
            select(StudentDailyTask)
            .options(
                joinedload(StudentDailyTask.daily_task).joinedload(
                    DailyTask.question
                )
            )
            .where(
                StudentDailyTask.student_id == student_id,
                StudentDailyTask.task_date == task_date,
            )
        )
        if lock:
            statement = statement.with_for_update(of=StudentDailyTask)
        return await self.session.scalar(statement)

    @staticmethod
    def _response(assignment: StudentDailyTask) -> DailyTaskResponse:
        question: DailyTaskQuestion = assignment.daily_task.question
        return DailyTaskResponse(
            id=assignment.id,
            date=assignment.task_date,
            type=question.task_type,
            question=question.question,
            options=question.options,
            image_url=question.image_url,
            hotspots=question.hotspots,
            completed_at=assignment.completed_at,
            reward=question.reward,
        )
