from app.core.enums import HttpErrorMessage


_VALIDATION_ERROR_MESSAGES = {
    message.value: message
    for message in (
        HttpErrorMessage.GROUPS_NOT_FOUND,
        HttpErrorMessage.GROUP_HAS_TOO_MANY_TEACHERS,
        HttpErrorMessage.DUPLICATE_TEACHER_IDS,
        HttpErrorMessage.TEACHERS_NOT_FOUND,
        HttpErrorMessage.COURSE_ALREADY_EXISTS,
    )
}


def validation_error_message(
    error: ValueError,
    fallback: HttpErrorMessage,
) -> HttpErrorMessage:
    """Return a known client-facing validation message, never raw exception text."""
    return _VALIDATION_ERROR_MESSAGES.get(str(error), fallback)
