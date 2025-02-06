from fastapi import APIRouter, Depends, Query

from application.auth.depends import get_current_user
from application.user.model import User

from ..base.exceptions import get_403_http_exception, get_404_http_exception, get_409_http_exception
from ..base.schemas import PaginatedResponse
from .dao import PostDAO
from .messages import POST_DELETED, POST_NOT_AUTHOR, POST_NOT_FOUND, POST_TIMEOUT
from .schemas import PostCreateSchema, PostGetSchema, PostUpdateSchema

post_router = APIRouter(
    prefix="/posts",
    tags=["Публикации"],
    dependencies=[Depends(get_current_user)],
)


@post_router.post("/", response_model=PostGetSchema)
async def create_post(post_data: PostCreateSchema, current_user: User = Depends(get_current_user)):
    data = post_data.model_dump()
    data["user_id"] = current_user.id
    post = await PostDAO.add(**data)
    post.user = current_user
    return post


@post_router.get("/", response_model=PaginatedResponse[PostGetSchema])
async def get_posts(page: int = Query(1, ge=1)):
    posts = await PostDAO.find_all(page=page)
    result = {
        "items": posts,
        "page": page,
        "count": len(posts),
    }
    return result


@post_router.get("/{post_id}", response_model=PostGetSchema)
async def get_post(post_id: int):
    filters = dict(id=post_id)
    post = await PostDAO.find_one_or_none(filters=filters)
    if not post:
        raise get_404_http_exception(POST_NOT_FOUND)

    return post


@post_router.put("/{post_id}", response_model=PostGetSchema)
async def update_post(post_id: int, post_data: PostUpdateSchema, current_user: User = Depends(get_current_user)):
    filters = dict(id=post_id)
    post = await PostDAO.find_one_or_none(filters=filters)
    if not post:
        raise get_404_http_exception(POST_NOT_FOUND)

    if post.user_id != current_user.id:
        raise get_403_http_exception(POST_NOT_AUTHOR)

    if not post.can_update():
        raise get_409_http_exception(POST_TIMEOUT)

    data = post_data.model_dump()
    updated_post = await PostDAO.update(instance=post, **data)

    return updated_post


@post_router.delete("/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user)):
    filters = dict(id=post_id)
    post = await PostDAO.find_one_or_none(filters=filters)
    if not post:
        raise get_404_http_exception(POST_NOT_FOUND)

    if post.user_id != current_user.id:
        raise get_403_http_exception(POST_NOT_AUTHOR)

    await PostDAO.delete(instance=post)
    return {"message": POST_DELETED}
