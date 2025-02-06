from fastapi import HTTPException
from sqlalchemy.exc import StatementError
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from application.admin.messages import NOT_ADMIN


def get_401_http_exception(detail: str) -> HTTPException:
    ex = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail=detail,
    )
    return ex


def get_403_http_exception(detail: str = NOT_ADMIN) -> HTTPException:
    ex = HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail=detail,
    )
    return ex


def get_404_http_exception(detail: str) -> HTTPException:
    ex = HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail=detail,
    )
    return ex


def get_409_http_exception(detail: str) -> HTTPException:
    ex = HTTPException(
        status_code=HTTP_409_CONFLICT,
        detail=detail,
    )
    return ex


def get_original_error(ex: StatementError) -> Exception | None:
    return ex.orig.__cause__


class BaseAppException(Exception):
    """Базовый класс ошибки для приложения"""

    def __init__(self, msg: str = None, details: dict = None):
        self.msg = msg
        self.details = details

    def __str__(self):
        return self.msg
