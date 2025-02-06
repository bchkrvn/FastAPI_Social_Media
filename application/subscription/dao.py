from asyncpg import CheckViolationError, UniqueViolationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from application.base.dao import BaseDAO

from ..base.exceptions import get_original_error
from .exceptions import ReSubscriptionError, SubscriptionForYourselfError
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
            original_error = get_original_error(ex)

            if isinstance(original_error, UniqueViolationError):
                raise ReSubscriptionError(data)
            elif isinstance(original_error, CheckViolationError):
                raise SubscriptionForYourselfError(data)

            raise ex
