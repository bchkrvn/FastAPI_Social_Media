from application.dao.base import BaseDAO

from .model import User


class UsersDAO(BaseDAO):
    model = User
