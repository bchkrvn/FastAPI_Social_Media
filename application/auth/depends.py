from datetime import datetime, timezone

from fastapi import Depends, Request
from jose import JWTError

from application.auth.constants import COOKIES_TOKEN_KEY, TOKEN_EXPIRED_KEY, USER_ID_KEY
from application.auth.messages import EXPIRED_TOKEN, NOT_VALID_TOKEN_DATA, TOKEN_NOT_FOUND, TOKEN_NOT_VALID
from application.auth.services import decode_access_token
from application.base.exceptions import get_401_http_exception
from application.user.dao import UserDAO
from application.user.messages import USER_NOT_ACTIVE, USER_NOT_FOUND
from application.user.model import User


def get_token(request: Request) -> str:
    token = request.cookies.get(COOKIES_TOKEN_KEY)
    if not token:
        ex = get_401_http_exception(TOKEN_NOT_FOUND)
        raise ex

    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    try:
        user_data = decode_access_token(token)
    except JWTError:
        raise get_401_http_exception(TOKEN_NOT_VALID)

    expire = user_data.get(TOKEN_EXPIRED_KEY)
    user_id = user_data.get(USER_ID_KEY)
    is_valid = (
        isinstance(expire, int),
        isinstance(user_id, int),
    )

    if not all(is_valid):
        raise get_401_http_exception(NOT_VALID_TOKEN_DATA)

    is_expired = datetime.fromtimestamp(expire, tz=timezone.utc) < datetime.now(tz=timezone.utc)
    if is_expired:
        raise get_401_http_exception(EXPIRED_TOKEN)

    filters = dict(id=user_id)
    user = await UserDAO.find_one_or_none(filters=filters)
    if not user:
        raise get_401_http_exception(USER_NOT_FOUND)

    if not user.is_active:
        raise get_401_http_exception(USER_NOT_ACTIVE)

    return user
