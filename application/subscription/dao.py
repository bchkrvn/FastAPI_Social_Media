from asyncpg import CheckViolationError, ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from application.base.dao import BaseDAO

from ..base.exceptions import get_original_error
from ..db.session import connection
from .exceptions import BloggerNotFoundError, FollowerNotFoundError, ReSubscriptionError, SubscriptionForYourselfError
from .model import Subscription


class SubscriptionDAO(BaseDAO):
    model = Subscription
    options = [
        joinedload(model.follower),
        joinedload(model.blogger),
    ]

    @classmethod
    async def add(cls, **data) -> Subscription:
        try:
            return await super().add(**data)
        except IntegrityError as ex:
            cls.__raise_error(ex, data)

    @classmethod
    def __raise_error(cls, ex: IntegrityError, data: dict):
        original_error = get_original_error(ex)

        if isinstance(original_error, UniqueViolationError):
            raise ReSubscriptionError(data)

        elif isinstance(original_error, CheckViolationError):
            raise SubscriptionForYourselfError(data)

        elif isinstance(original_error, ForeignKeyViolationError):
            if "blogger_id" in original_error.detail:
                raise BloggerNotFoundError(data)
            elif "follower_id" in original_error.detail:
                raise FollowerNotFoundError(data)

        raise ex

    @classmethod
    @connection
    async def get_followers_count(cls, session: AsyncSession, user_id: int):
        followers_query = select(func.count()).select_from(cls.model).filter_by(blogger_id=user_id)
        followers_count = await session.scalar(followers_query)
        return followers_count

    @classmethod
    @connection
    async def get_subscriptions_count(cls, session: AsyncSession, user_id: int):
        subscriptions_query = select(func.count()).select_from(cls.model).filter_by(follower_id=user_id)
        subscriptions_count = await session.scalar(subscriptions_query)
        return subscriptions_count
