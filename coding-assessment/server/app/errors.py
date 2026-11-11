from typing import Any, NoReturn


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def not_implemented(fn: str) -> NoReturn:
    raise AppError(501, "NOT_IMPLEMENTED", f"{fn} is not implemented")


def bad_request(message: str, details: Any = None) -> NoReturn:
    raise AppError(400, "BAD_REQUEST", message, details)


def unauthorized(message: str = "Unauthorized") -> NoReturn:
    raise AppError(401, "UNAUTHORIZED", message)


def forbidden(message: str = "Forbidden") -> NoReturn:
    raise AppError(403, "FORBIDDEN", message)


def not_found(resource: str, id: str | None = None) -> NoReturn:
    message = f"{resource} {id} not found" if id else f"{resource} not found"
    raise AppError(404, "NOT_FOUND", message)


def conflict(message: str) -> NoReturn:
    raise AppError(409, "CONFLICT", message)
