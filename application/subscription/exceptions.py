from application.base.exceptions import BaseAppException
from application.subscription.messages import (
    BLOGGER_NOT_FOUND_ERROR,
    FOLLOWER_NOT_FOUND_ERROR,
    RE_SUBSCRIBE_ERROR,
    SUBSCRIBE_FOR_YOURSELF_ERROR,
)


class ReSubscriptionError(BaseAppException):
    """Ошибка повторной подписки на пользователя"""

    def __init__(self, details: dict):
        self.msg = RE_SUBSCRIBE_ERROR
        self.details = details


class SubscriptionForYourselfError(BaseAppException):
    """Ошибка подписки на самого себя"""

    def __init__(self, details: dict):
        self.msg = SUBSCRIBE_FOR_YOURSELF_ERROR
        self.details = details


class BloggerNotFoundError(BaseAppException):
    """Не найден пользователь, на которого хотят подписаться"""

    def __init__(self, details: dict):
        self.msg = BLOGGER_NOT_FOUND_ERROR
        self.details = details


class FollowerNotFoundError(BaseAppException):
    """Не найден подписчик"""

    def __init__(self, details: dict):
        self.msg = FOLLOWER_NOT_FOUND_ERROR
        self.details = details
