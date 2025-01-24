from fastapi import HTTPException
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
