from fastapi import APIRouter, Query

from application.base.exceptions import get_404_http_exception
from application.base.schemas import PaginatedResponse, get_paginated_response
from application.post.dao import PostDAO
from application.post.messages import POST_DELETED, POST_NOT_FOUND
from application.post.schemas import PostGetSchema

post_admin_router = APIRouter(
    prefix="/posts",
    tags=["Управление публикациями"],
    include_in_schema=False,
)


@post_admin_router.get("/", response_model=PaginatedResponse[PostGetSchema])
async def all_posts(page: int = Query(1, ge=1)):
    posts = await PostDAO.find_all(page=page)
    return get_paginated_response(posts, page)


@post_admin_router.get("/{post_id:int}", response_model=PostGetSchema)
async def get_post(post_id: int):
    filters = dict(id=post_id)
    post = await PostDAO.find_one_or_none(filters=filters)
    if not post:
        raise get_404_http_exception(POST_NOT_FOUND)

    return post


@post_admin_router.delete("/{post_id:int}")
async def delete_post(post_id: int):
    filters = dict(id=post_id)
    post = await PostDAO.find_one_or_none(filters=filters)
    if not post:
        raise get_404_http_exception(POST_NOT_FOUND)

    await PostDAO.delete(instance=post)
    return {"message": POST_DELETED}
