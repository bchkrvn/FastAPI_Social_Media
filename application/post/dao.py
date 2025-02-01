from sqlalchemy.orm import joinedload

from application.base.dao import BaseDAO

from .model import Post


class PostDAO(BaseDAO):
    model = Post
    options = [
        joinedload(model.user),
    ]
