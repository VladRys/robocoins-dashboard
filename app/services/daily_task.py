from datetime import date, datetime, timezone

from sqlalchemy import case, select, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import BalanceChangeReasons
from app.models.course import Course
from app.models.daily_task import (
    CourseDailyTask,
    DailyTask,
    DailyTaskQuestion,
    StudentDailyTask,
)
from app.models.student import Student
from app.models.transaction import BalanceTransaction
from app.schemas.daily_task import (
    DailyTaskAnswerResponse,
    DailyTaskResponse,
    DailyTaskTestAnswerResponse,
    DailyTaskTestResponse,
)


class DailyTaskNotFoundError(Exception):
    pass


class DailyTaskAlreadyCompletedError(Exception):
    pass


class StudentNotFoundError(Exception):
    pass


class DailyTaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_test_tasks(self) -> list[DailyTaskTestResponse]:
        tasks = (
            await self.session.scalars(
                select(DailyTask)
                .options(joinedload(DailyTask.question))
                .order_by(DailyTask.id.asc())
            )
        ).all()
        return [
            DailyTaskTestResponse(
                id=task.id,
                type=task.question.task_type,
                question=task.question.question,
                options=task.question.options,
                image_url=task.question.image_url,
                hotspots=task.question.hotspots,
                reward=task.question.reward,
            )
            for task in tasks
        ]

    async def answer_test_task(
        self,
        task_id: int,
        answer: str,
    ) -> DailyTaskTestAnswerResponse:
        question = await self.session.scalar(
            select(DailyTaskQuestion)
            .join(DailyTask, DailyTask.question_id == DailyTaskQuestion.id)
            .where(DailyTask.id == task_id)
        )
        if question is None:
            raise DailyTaskNotFoundError
        return DailyTaskTestAnswerResponse(
            correct=answer.strip().casefold() == question.answer.strip().casefold()
        )

    async def get_or_create(self, student_id: int) -> DailyTaskResponse:
        assignments = await self.get_or_create_all(student_id)
        if not assignments:
            raise DailyTaskNotFoundError
        return assignments[0]

    async def get_or_create_all(self, student_id: int) -> list[DailyTaskResponse]:
        today = date.today()
        student = await self.session.scalar(
            select(Student)
            .options(selectinload(Student.groups))
            .where(Student.id == student_id)
            .with_for_update()
        )
        if student is None:
            raise StudentNotFoundError

        course_ids = sorted({group.course_id for group in student.groups})
        assignments: list[DailyTaskResponse] = []
        if not course_ids:
            assignment = await self._get_assignment(student_id, today)
            if assignment is None:
                task = await self._select_task(set())
                task.last_date = today
                assignment = StudentDailyTask(
                    student_id=student_id,
                    daily_task=task,
                    task_date=today,
                )
                self.session.add(assignment)
                await self.session.commit()
                await self.session.refresh(assignment)
            return [self._response(assignment)]

        for course_id in course_ids:
            course_assignment = await self._get_course_assignment(course_id, today)
            assignment = await self._get_assignment(
                student_id,
                today,
                course_id=course_id,
            )
            if assignment is None:
                if course_assignment is None:
                    await self.session.scalar(
                        select(Course)
                        .where(Course.id == course_id)
                        .with_for_update()
                    )
                    course_assignment = await self._get_course_assignment(
                        course_id,
                        today,
                    )
                if course_assignment is None:
                    task = await self._select_task({course_id})
                    task.last_date = today
                    course_assignment = CourseDailyTask(
                        course_id=course_id,
                        daily_task=task,
                        task_date=today,
                    )
                    self.session.add(course_assignment)
                assignment = StudentDailyTask(
                    student_id=student_id,
                    course_id=course_id,
                    daily_task=course_assignment.daily_task,
                    task_date=today,
                )
                self.session.add(assignment)
            assignments.append(assignment)

        await self.session.commit()
        for assignment in assignments:
            await self.session.refresh(assignment)
        return [self._response(assignment) for assignment in assignments]

    async def _select_task(self, course_ids: set[int]) -> DailyTask:
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
                if not candidate.question.course_ids
                or course_ids.intersection(candidate.question.course_ids)
            ),
            None,
        )
        if task is None:
            raise DailyTaskNotFoundError
        return task

    async def answer(
        self,
        student_id: int,
        answer: str,
        *,
        course_id: int | None = None,
    ) -> DailyTaskAnswerResponse:
        assignment = await self._get_assignment(
            student_id,
            date.today(),
            course_id=course_id,
            first_available=course_id is None,
            lock=True,
        )
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
        course_id: int | None = None,
        first_available: bool = False,
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
        if first_available:
            statement = statement.order_by(
                StudentDailyTask.course_id.asc().nullslast()
            )
        else:
            statement = statement.where(StudentDailyTask.course_id == course_id)
        if lock:
            statement = statement.with_for_update(of=StudentDailyTask)
        return await self.session.scalar(statement)

    async def _get_course_assignment(
        self,
        course_id: int,
        task_date: date,
    ) -> CourseDailyTask | None:
        return await self.session.scalar(
            select(CourseDailyTask)
            .options(
                joinedload(CourseDailyTask.daily_task).joinedload(
                    DailyTask.question
                )
            )
            .where(
                CourseDailyTask.course_id == course_id,
                CourseDailyTask.task_date == task_date,
            )
        )

    @staticmethod
    def _response(assignment: StudentDailyTask) -> DailyTaskResponse:
        question: DailyTaskQuestion = assignment.daily_task.question
        return DailyTaskResponse(
            id=assignment.id,
            date=assignment.task_date,
            course_id=assignment.course_id,
            type=question.task_type,
            question=question.question,
            options=question.options,
            image_url=question.image_url,
            hotspots=question.hotspots,
            completed_at=assignment.completed_at,
            reward=question.reward,
        )
