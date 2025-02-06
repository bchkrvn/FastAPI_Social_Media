import pytest

from application.subscription.dao import SubscriptionDAO
from application.subscription.exceptions import (
    BloggerNotFoundError,
    FollowerNotFoundError,
    ReSubscriptionError,
    SubscriptionForYourselfError,
)


class TestSubscriptionDAO:
    @pytest.mark.anyio
    async def test_success(self, user, user_2, drop_subscription_table):
        subscription_data = {
            "follower_id": user.id,
            "blogger_id": user_2.id,
        }
        subscription = await SubscriptionDAO.add(**subscription_data)

        assert subscription.follower_id == user.id
        assert subscription.blogger_id == user_2.id

    @pytest.mark.anyio
    async def test_blogger_not_found(self, user):
        subscription_data = {
            "follower_id": user.id,
            "blogger_id": 999999,
        }
        with pytest.raises(BloggerNotFoundError):
            await SubscriptionDAO.add(**subscription_data)

    @pytest.mark.anyio
    async def test_follower_not_found(self, user):
        subscription_data = {
            "follower_id": 999999999,
            "blogger_id": user.id,
        }
        with pytest.raises(FollowerNotFoundError):
            await SubscriptionDAO.add(**subscription_data)

    @pytest.mark.anyio
    async def test_double_subscribe(self, user, user_2):
        subscription_data = {
            "follower_id": user.id,
            "blogger_id": user_2.id,
        }

        await SubscriptionDAO.add(**subscription_data)

        with pytest.raises(ReSubscriptionError):
            await SubscriptionDAO.add(**subscription_data)

    @pytest.mark.anyio
    async def test_subscribe_for_yourself(self, user):
        subscription_data = {
            "follower_id": user.id,
            "blogger_id": user.id,
        }

        with pytest.raises(SubscriptionForYourselfError):
            await SubscriptionDAO.add(**subscription_data)
