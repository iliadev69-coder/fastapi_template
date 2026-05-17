from collections.abc import Callable, Coroutine
from http import HTTPStatus
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.resources.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    FKNotFoundError,
    NotFoundError,
    ValidationError,
)


def _base_error_handler(
    status: HTTPStatus,
) -> Callable[[Request, Exception], Coroutine[Any, Any, JSONResponse]]:
    async def _error_handler(  # noqa: RUF029
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        try:
            detail = exc.args[0]
        except IndexError:
            detail = status.phrase
        return JSONResponse(status_code=status, content={'detail': detail})

    return _error_handler


exception_handlers: dict[
    type[Exception] | int,
    Callable[[Request, Exception], Coroutine[Any, Any, Response]],
] = {
    AlreadyExistsError: _base_error_handler(HTTPStatus.CONFLICT),
    AuthenticationError: _base_error_handler(HTTPStatus.UNAUTHORIZED),
    AuthorizationError: _base_error_handler(HTTPStatus.FORBIDDEN),
    FKNotFoundError: _base_error_handler(HTTPStatus.BAD_REQUEST),
    NotFoundError: _base_error_handler(HTTPStatus.NOT_FOUND),
    ValidationError: _base_error_handler(HTTPStatus.BAD_REQUEST),
}
