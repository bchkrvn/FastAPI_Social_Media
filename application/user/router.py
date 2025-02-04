from fastapi import APIRouter, Depends, Response

from application.auth.constants import COOKIES_TOKEN_KEY
from application.auth.depends import get_current_user
from application.base.exceptions import get_409_http_exception
from application.user.dao import UserDAO
from application.user.messages import NOT_UNIQUE_USER, PASSWORD_NOT_VALID, SUCCESS_DELETE, SUCCESS_PASSWORD_CHANGE
from application.user.model import User
from application.user.password import get_password_hash, verify_password
from application.user.schemas import SchemaChangePassword, SchemaMeGet, SchemaMePut

user_router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@user_router.get("/me", response_model=SchemaMeGet)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.put("/me", response_model=SchemaMeGet)
async def me_update(user_data: SchemaMePut, current_user: User = Depends(get_current_user)) -> dict:
    filters = dict(email=user_data.email)
    user = await UserDAO.find_one_or_none(filters=filters)
    if user and user.id != current_user.id:
        detail = NOT_UNIQUE_USER.format(user_data.email)
        raise get_409_http_exception(detail)

    user_dict = user_data.model_dump(exclude_none=True)
    updated_user = await UserDAO.update(current_user, **user_dict)

    return updated_user


@user_router.delete("/me")
async def me_delete(response: Response, current_user: User = Depends(get_current_user)) -> dict:
    await UserDAO.deactivate(current_user)
    response.delete_cookie(key=COOKIES_TOKEN_KEY)
    return {"message": SUCCESS_DELETE}


@user_router.post("/me/change_password")
async def change_password(
    password_schema: SchemaChangePassword,
    current_user: User = Depends(get_current_user),
) -> dict:
    old_password = password_schema.old_password
    is_valid = verify_password(old_password, current_user.password)
    if not is_valid:
        raise get_409_http_exception(PASSWORD_NOT_VALID)

    current_user.password = get_password_hash(password_schema.password)
    await UserDAO.update(current_user)
    return {"message": SUCCESS_PASSWORD_CHANGE}
