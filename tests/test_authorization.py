import asyncio
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes.group import assign_group_student, remove_group_student
from app.api.routes.student import edit_student_avatar, edit_student_nickname
from app.core.database import Base
from app.core.enums import AuthorizationAction, UserRole
from app.models.course import Course
from app.models.group import Group
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.repositories.group import GroupRepository
from app.repositories.student import StudentRepository
from app.schemas.group import GroupStudentAssignmentRequest
from app.schemas.student import StudentAvatarEditRequest, StudentNicknameEditRequest
from app.services.authorization import AuthorizationService
from app.services.group import GroupService
from app.services.student import StudentService


def test_authorization_policies_and_scoped_avatar_and_group_actions(tmp_path: Path):
    async def run_test():
        engine = create_async_engine(
            URL.create("sqlite+aiosqlite", database=str(tmp_path / "authorization.db"))
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async with session_factory() as session:
                course = Course(name="Robotics")
                session.add(course)
                await session.flush()

                admin = User(name="Admin", role=UserRole.ADMIN.value, access_code="ADMIN001")
                teacher = User(name="Teacher", role=UserRole.TEACHER.value, access_code="TEACHER01")
                other_teacher = User(
                    name="Other Teacher",
                    role=UserRole.TEACHER.value,
                    access_code="TEACHER02",
                )
                student = User(name="Student", role=UserRole.STUDENT.value, access_code="STUDENT01")
                other_student = User(
                    name="Other Student",
                    role=UserRole.STUDENT.value,
                    access_code="STUDENT02",
                )
                session.add_all([admin, teacher, other_teacher, student, other_student])
                await session.flush()

                session.add_all([Teacher(user_id=teacher.id), Teacher(user_id=other_teacher.id)])
                student_profile = Student(
                    id=student.id,
                    user_id=student.id,
                    name=student.name,
                    avatar="🤖",
                    balance=0.0,
                    hash_access_key="student-hash-1",
                    access_code="STU00001",
                )
                other_student_profile = Student(
                    id=other_student.id,
                    user_id=other_student.id,
                    name=other_student.name,
                    avatar="🦊",
                    balance=0.0,
                    hash_access_key="student-hash-2",
                    access_code="STU00002",
                )
                session.add_all([student_profile, other_student_profile])
                await session.flush()

                teacher_group = Group(
                    name="Teacher's group",
                    course_id=course.id,
                    teacher_1_id=teacher.id,
                    students=[student_profile],
                )
                other_group = Group(
                    name="Other group",
                    course_id=course.id,
                    teacher_1_id=other_teacher.id,
                    students=[other_student_profile],
                )
                session.add_all([teacher_group, other_group])
                await session.commit()

                student_service = StudentService(session, StudentRepository(session))
                group_service = GroupService(session, GroupRepository(session))
                authorization = AuthorizationService(student_service, group_service)

                assert await authorization.is_allowed(
                    AuthorizationAction.VIEW_STUDENT_CREDENTIALS,
                    student,
                    student.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.ACCESS_DAILY_TASK,
                    student,
                    student.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.ACCESS_DAILY_TASK,
                    student,
                    other_student.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.VIEW_STUDENT_CREDENTIALS,
                    teacher,
                    student.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.ACCESS_DAILY_TASK,
                    teacher,
                    student.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_AVATAR,
                    student,
                    student.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_NICKNAME,
                    student,
                    student.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_AVATAR,
                    student,
                    other_student.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_AVATAR,
                    teacher,
                    student.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_AVATAR,
                    teacher,
                    other_student.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_NICKNAME,
                    teacher,
                    other_student.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.EDIT_STUDENT_AVATAR,
                    admin,
                    other_student.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.ASSIGN_STUDENT_TO_GROUP,
                    teacher,
                    teacher_group.id,
                )
                assert not await authorization.is_allowed(
                    AuthorizationAction.ASSIGN_STUDENT_TO_GROUP,
                    teacher,
                    other_group.id,
                )
                assert await authorization.is_allowed(
                    AuthorizationAction.ASSIGN_STUDENT_TO_GROUP,
                    admin,
                    other_group.id,
                )

                updated_profile = await edit_student_avatar(
                    student.id,
                    StudentAvatarEditRequest(new_avatar="🐸"),
                    service=student_service,
                    user=teacher,
                    authorization=authorization,
                )
                assert updated_profile.avatar == "🐸"

                with pytest.raises(HTTPException) as denied_avatar:
                    await edit_student_avatar(
                        other_student.id,
                        StudentAvatarEditRequest(new_avatar="🐼"),
                        service=student_service,
                        user=teacher,
                        authorization=authorization,
                    )
                assert denied_avatar.value.status_code == 403

                updated_profile = await edit_student_nickname(
                    student.id,
                    StudentNicknameEditRequest(new_nickname="Updated Student"),
                    service=student_service,
                    user=teacher,
                    authorization=authorization,
                )
                assert updated_profile.name == "Updated Student"
                assert (await session.get(User, student.id)).name == "Updated Student"

                with pytest.raises(HTTPException) as denied_nickname:
                    await edit_student_nickname(
                        other_student.id,
                        StudentNicknameEditRequest(new_nickname="Unauthorized"),
                        service=student_service,
                        user=teacher,
                        authorization=authorization,
                    )
                assert denied_nickname.value.status_code == 403

                with pytest.raises(HTTPException) as denied_assignment:
                    await assign_group_student(
                        other_group.id,
                        GroupStudentAssignmentRequest(student_id=student.id),
                        service=group_service,
                        user=teacher,
                        authorization=authorization,
                    )
                assert denied_assignment.value.status_code == 403

                with pytest.raises(HTTPException) as denied_removal:
                    await remove_group_student(
                        other_group.id,
                        other_student.id,
                        service=group_service,
                        user=teacher,
                        authorization=authorization,
                    )
                assert denied_removal.value.status_code == 403

                assigned_group = await assign_group_student(
                    teacher_group.id,
                    GroupStudentAssignmentRequest(student_id=other_student.id),
                    service=group_service,
                    user=teacher,
                    authorization=authorization,
                )
                assert {profile.id for profile in assigned_group.students} == {
                    student.id,
                    other_student.id,
                }

                updated_group = await remove_group_student(
                    teacher_group.id,
                    other_student.id,
                    service=group_service,
                    user=teacher,
                    authorization=authorization,
                )
                assert {profile.id for profile in updated_group.students} == {student.id}
        finally:
            await engine.dispose()

    asyncio.run(run_test())
