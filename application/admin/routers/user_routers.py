from fastapi import APIRouter, Query

from application.base.exceptions import get_404_http_exception, get_409_http_exception
from application.base.schemas import PaginatedResponse
from application.user.dao import UsersDAO
from application.user.messages import (
    SUCCESS_ACTIVATE,
    SUCCESS_DEACTIVATE,
    USER_ALREADY_ACTIVE,
    USER_ALREADY_DEACTIVE,
    USER_NOT_FOUND,
)
from application.user.schemas import SchemaMeGet

user_admin_router = APIRouter(
    prefix="/users",
    tags=["Управление пользователями"],
    include_in_schema=False,
    dependencies=[],
)


@user_admin_router.get("/", response_model=PaginatedResponse[SchemaMeGet])
async def all_users(page: int = Query(1, ge=1)):
    users = await UsersDAO.find_all(page=page)
    result = {
        "items": users,
        "page": page,
        "count": len(users),
    }
    return result


@user_admin_router.get("/{id_:int}", response_model=SchemaMeGet)
async def user_id(id_: int):
    filters = dict(id=id_)
    user = await UsersDAO.find_one_or_none(filters=filters)
    if not user:
        raise get_404_http_exception(USER_NOT_FOUND)
    return user


@user_admin_router.get("/{id_:int}/activate")
async def activate_user(id_: int):
    filters = dict(id=id_)
    user = await UsersDAO.find_one_or_none(filters=filters)
    if not user:
        raise get_404_http_exception(USER_NOT_FOUND)

    if user.is_active:
        raise get_409_http_exception(USER_ALREADY_ACTIVE)

    await UsersDAO.activate(user)
    return {"message": SUCCESS_ACTIVATE}


@user_admin_router.get("/{id_:int}/deactivate")
async def deactivate_user(id_: int):
    filters = dict(id=id_)
    user = await UsersDAO.find_one_or_none(filters=filters)
    if not user:
        raise get_404_http_exception(USER_NOT_FOUND)

    if not user.is_active:
        raise get_409_http_exception(USER_ALREADY_DEACTIVE)

    await UsersDAO.deactivate(user)
    return {"message": SUCCESS_DEACTIVATE}
