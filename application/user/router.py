from fastapi import APIRouter, Depends, Response

from application.auth.constants import COOKIES_TOKEN_KEY
from application.auth.depends import get_current_user
from application.base.exceptions import get_409_http_exception
from application.user.dao import UserDAO
from application.user.messages import NOT_UNIQUE_USER, SUCCESS_DELETE
from application.user.model import User
from application.user.schemas import SchemaMeGet, SchemaMePut

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
