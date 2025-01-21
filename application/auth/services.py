from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request
from jose import JWTError, jwt

from application.auth.exceptions import (
    EXPIRED_TOKEN,
    NOT_VALID_DATA,
    TOKEN_NOT_FOUND,
    TOKEN_NOT_VALID,
    USER_NOT_FOUND,
    get_401_http_exception,
    get_403_http_exception,
)
from application.auth.schemas import SchemaLogin
from application.config import settings
from application.user.dao import UsersDAO
from application.user.model import User
from application.user.password import verify_password

USER_ID_KEY = "user_id"
TOKEN_EXPIRED_KEY = "exp"
COOKIES_TOKEN_KEY = "access_token"


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        USER_ID_KEY: user.id,
        TOKEN_EXPIRED_KEY: expire,
    }
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


async def auth_user(user_data: SchemaLogin) -> User | None:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if not user:
        return None

    is_correct_password = verify_password(user_data.password, user.password)
    if not is_correct_password:
        return None

    return user


def get_token(request: Request) -> str:
    token = request.cookies.get(COOKIES_TOKEN_KEY)
    if not token:
        ex = get_401_http_exception(TOKEN_NOT_FOUND)
        raise ex

    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    try:
        user_data = _decode_access_token(token)
    except JWTError:
        raise get_401_http_exception(TOKEN_NOT_VALID)

    expire = user_data.get(TOKEN_EXPIRED_KEY)
    user_id = user_data.get(USER_ID_KEY)
    is_valid = (
        isinstance(expire, int),
        isinstance(user_id, int),
    )

    if not all(is_valid):
        raise get_401_http_exception(NOT_VALID_DATA)

    is_expired = datetime.fromtimestamp(expire, tz=timezone.utc) < datetime.now(tz=timezone.utc)
    if is_expired:
        raise get_401_http_exception(EXPIRED_TOKEN)

    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        raise get_401_http_exception(USER_NOT_FOUND)

    return user


def _decode_access_token(token: str) -> dict:
    user_data = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "verify_exp": False,
        },
    )
    return user_data


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise get_403_http_exception()

    return user
