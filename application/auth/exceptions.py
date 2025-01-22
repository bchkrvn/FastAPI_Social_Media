from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

TOKEN_NOT_FOUND = "Токен не найден"
TOKEN_NOT_VALID = "Токен не валидный"
NOT_VALID_DATA = "Не валидные данные в токене"
EXPIRED_TOKEN = "Токен истек"
USER_NOT_FOUND = "Пользователь не найден"
NOT_ADMIN = "У вас недостаточно прав для этого действия"
NOT_UNIQUE_USER = "Пользователь с почтой {} уже существует"
NOT_VALID_EMAIL_OR_PASSWORD = "Неверная почта или пароль"


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
