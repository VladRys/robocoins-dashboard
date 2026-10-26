from types import SimpleNamespace


def student_with_groups(
    *,
    student_id: int,
    name: str,
    group_id: int = 1,
    course_name: str = "Python",
    avatar: str | None = None,
    balance: float = 0.0,
    hash_access_key: str = "test-hash",
    access_code: str = "ABC12345",
) -> SimpleNamespace:
    """Lightweight student stand-in for route unit tests."""
    course = SimpleNamespace(name=course_name)
    group = SimpleNamespace(id=group_id, course=course)
    return SimpleNamespace(
        id=student_id,
        user_id=student_id,
        name=name,
        groups=[group],
        avatar=avatar,
        balance=balance,
        hash_access_key=hash_access_key,
        access_code=access_code,
    )
