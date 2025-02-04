from fastapi import APIRouter, Response

from application.base.exceptions import get_401_http_exception, get_409_http_exception
from application.user.dao import UserDAO
from application.user.messages import NOT_UNIQUE_USER, USER_NOT_ACTIVE
from application.user.password import get_password_hash

from .constants import COOKIES_TOKEN_KEY
from .messages import NOT_VALID_EMAIL_OR_PASSWORD, SUCCESS_LOGOUT, SUCCESS_REGISTRATION
from .schemas import SchemaLogin, SchemaRegister
from .services import auth_user, create_access_token

auth_router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@auth_router.post("/register")
async def register_user(user_data: SchemaRegister) -> dict:
    filters = dict(email=user_data.email)
    user = await UserDAO.find_one_or_none(filters=filters)
    if user:
        detail = NOT_UNIQUE_USER.format(user_data.email)
        raise get_409_http_exception(detail)

    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_data.password)
    del user_dict["password2"]
    await UserDAO.add(**user_dict)

    return {"message": SUCCESS_REGISTRATION}


@auth_router.post("/login")
async def login(response: Response, user_data: SchemaLogin) -> dict:
    user = await auth_user(user_data)
    if not user:
        raise get_401_http_exception(NOT_VALID_EMAIL_OR_PASSWORD)

    if not user.is_active:
        raise get_401_http_exception(USER_NOT_ACTIVE)

    access_token = create_access_token(user)
    response.set_cookie(
        key=COOKIES_TOKEN_KEY,
        value=access_token,
        httponly=True,
    )

    return {COOKIES_TOKEN_KEY: access_token}


@auth_router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIES_TOKEN_KEY)
    return {"message": SUCCESS_LOGOUT}
