from fastapi import APIRouter, Depends, HTTPException, Response
from starlette.status import HTTP_409_CONFLICT

from application.auth.exceptions import NOT_UNIQUE_USER
from application.auth.services import COOKIES_TOKEN_KEY, get_current_user
from application.user.dao import UsersDAO
from application.user.messages import SUCCESS_DELETE
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
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user and user.id != current_user.id:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=NOT_UNIQUE_USER.format(user_data.email))

    user_dict = user_data.model_dump(exclude_none=True)
    updated_user = await UsersDAO.update(current_user, **user_dict)

    return updated_user


@user_router.delete("/me")
async def me_delete(response: Response, current_user: User = Depends(get_current_user)) -> dict:
    await UsersDAO.delete(current_user)
    response.delete_cookie(key=COOKIES_TOKEN_KEY)

    return {"message": SUCCESS_DELETE}
