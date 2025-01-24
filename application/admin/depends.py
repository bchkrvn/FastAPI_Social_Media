from fastapi import Depends

from application.auth.depends import get_current_user
from application.base.exceptions import get_403_http_exception
from application.user.model import User


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise get_403_http_exception()

    return user
