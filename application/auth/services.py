from datetime import datetime, timedelta, timezone

from jose import jwt

from application.auth.constants import TOKEN_EXPIRED_KEY, USER_ID_KEY
from application.auth.schemas import SchemaLogin
from application.config import settings
from application.user.dao import UserDAO
from application.user.model import User
from application.user.password import verify_password


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        USER_ID_KEY: user.id,
        TOKEN_EXPIRED_KEY: expire,
    }
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


async def auth_user(user_data: SchemaLogin) -> User | None:
    filters = dict(email=user_data.email)
    user = await UserDAO.find_one_or_none(filters=filters)
    if not user:
        return None

    is_correct_password = verify_password(user_data.password, user.password)
    if not is_correct_password:
        return None

    return user


def decode_access_token(token: str) -> dict:
    user_data = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "verify_exp": False,
        },
    )
    return user_data
