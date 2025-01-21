from fastapi import APIRouter, HTTPException, Response
from starlette import status

from application.user.dao import UsersDAO
from application.user.password import get_password_hash

from .exceptions import NOT_UNIQUE_USER, NOT_VALID_EMAIL_OR_PASSWORD, get_401_http_exception
from .messages import SUCCESS_LOGOUT, SUCCESS_REGISTRATION
from .schemas import SchemaLogin, SchemaRegister
from .services import COOKIES_TOKEN_KEY, auth_user, create_access_token

auth_router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@auth_router.post("/register")
async def register_user(user_data: SchemaRegister) -> dict:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=NOT_UNIQUE_USER.format(user_data.email))

    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)

    return {"message": SUCCESS_REGISTRATION}


@auth_router.post("/login")
async def login(response: Response, user_data: SchemaLogin) -> dict:
    user = await auth_user(user_data)
    if not user:
        raise get_401_http_exception(NOT_VALID_EMAIL_OR_PASSWORD)

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
