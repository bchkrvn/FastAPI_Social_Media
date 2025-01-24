from fastapi import APIRouter, Depends, Query

from application.admin.depends import get_current_admin
from application.base.exceptions import get_404_http_exception
from application.base.schemas import PaginatedResponse
from application.user.dao import UsersDAO
from application.user.messages import USER_NOT_FOUND
from application.user.schemas import SchemaMeGet

admin_router = APIRouter(
    prefix="/admin", tags=["Панель администратора"], include_in_schema=False, dependencies=[Depends(get_current_admin)]
)


@admin_router.get("/all_users", response_model=PaginatedResponse[SchemaMeGet])
async def all_users(page: int = Query(1, ge=1)):
    users = await UsersDAO.find_all(page=page)
    result = dict(
        items=users,
        page=page,
        count=len(users),
    )
    return result


@admin_router.get("/users/{id_:int}", response_model=SchemaMeGet)
async def user_id(id_: int):
    user = await UsersDAO.find_one_or_none(id=id_)
    if not user:
        raise get_404_http_exception(USER_NOT_FOUND)
    return user
