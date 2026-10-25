from collections.abc import Sequence
from typing import Protocol

from app.core.enums import AuthorizationAction, UserRole
from app.models.user import User
from app.services.group import GroupService
from app.services.student import StudentService


class AuthorizationPolicy(Protocol):
    async def allows(self, user: User, subject_id: int | None) -> bool: ...


class RolePolicy:
    def __init__(self, *roles: UserRole) -> None:
        self._roles = {role.value for role in roles}

    async def allows(self, user: User, subject_id: int | None) -> bool:
        return user.role in self._roles


class OwnStudentResourcePolicy:
    async def allows(self, user: User, subject_id: int | None) -> bool:
        return (
            user.role == UserRole.STUDENT.value
            and subject_id is not None
            and user.id == subject_id
        )


class TeacherStudentGroupPolicy:
    def __init__(self, student_service: StudentService) -> None:
        self._student_service = student_service

    async def allows(self, user: User, subject_id: int | None) -> bool:
        return (
            user.role == UserRole.TEACHER.value
            and subject_id is not None
            and await self._student_service.is_student_in_teacher_group(
                subject_id,
                user.id,
            )
        )


class TeacherAssignedGroupPolicy:
    def __init__(self, group_service: GroupService) -> None:
        self._group_service = group_service

    async def allows(self, user: User, subject_id: int | None) -> bool:
        return (
            user.role == UserRole.TEACHER.value
            and subject_id is not None
            and await self._group_service.is_teacher_assigned_to_group(
                subject_id,
                user.id,
            )
        )


class AnyPolicy:
    def __init__(self, *policies: AuthorizationPolicy) -> None:
        self._policies: Sequence[AuthorizationPolicy] = policies

    async def allows(self, user: User, subject_id: int | None) -> bool:
        for policy in self._policies:
            if await policy.allows(user, subject_id):
                return True
        return False


class AuthorizationService:
    def __init__(
        self,
        student_service: StudentService,
        group_service: GroupService,
    ) -> None:
        edit_student_profile_policy = AnyPolicy(
            RolePolicy(UserRole.ADMIN),
            OwnStudentResourcePolicy(),
            TeacherStudentGroupPolicy(student_service),
        )
        self._policies: dict[AuthorizationAction, AuthorizationPolicy] = {
            AuthorizationAction.ADMINISTRATOR_OPERATION: RolePolicy(UserRole.ADMIN),
            AuthorizationAction.TEACHER_OPERATION: RolePolicy(UserRole.TEACHER),
            AuthorizationAction.VIEW_STUDENT_CREDENTIALS: RolePolicy(UserRole.STUDENT),
            AuthorizationAction.EDIT_STUDENT_AVATAR: edit_student_profile_policy,
            AuthorizationAction.EDIT_STUDENT_NICKNAME: edit_student_profile_policy,
            AuthorizationAction.ASSIGN_STUDENT_TO_GROUP: AnyPolicy(
                RolePolicy(UserRole.ADMIN),
                TeacherAssignedGroupPolicy(group_service),
            ),
        }

    async def is_allowed(
        self,
        action: AuthorizationAction,
        user: User,
        subject_id: int | None = None,
    ) -> bool:
        policy = self._policies.get(action)
        if policy is None:
            return False
        return await policy.allows(user, subject_id)
