import datetime

import pytest

from application.subscription.dao import SubscriptionDAO
from application.subscription.exceptions import ReSubscriptionError, SubscriptionForYourselfError
from application.user.dao import UserDAO


class TestSubscriptionDAO:
    @pytest.fixture(scope="function")
    async def get_data(self, drop_subscription_table, drop_user_table):
        follower_data = {
            "email": "follower@test.test",
            "password": "1234",
            "first_name": "test_name1",
            "last_name": "test_lastname1",
            "date_of_birth": datetime.date(year=2025, day=1, month=1),
        }
        await UserDAO.add(**follower_data)
        follower = await UserDAO.find_one_or_none(filters={"email": follower_data["email"]})

        blogger_data = {
            "email": "bloger@test.test",
            "password": "1234",
            "first_name": "test_name2",
            "last_name": "test_lastname2",
            "date_of_birth": datetime.date(year=2025, day=1, month=1),
        }
        await UserDAO.add(**blogger_data)
        blogger = await UserDAO.find_one_or_none(filters={"email": blogger_data["email"]})

        return follower, blogger

    @pytest.mark.anyio
    async def test_success(self, user, get_data):
        follower, blogger = get_data

        subscription_data = {
            "follower_id": follower.id,
            "blogger_id": blogger.id,
        }
        subscription = await SubscriptionDAO.add(**subscription_data)

        assert subscription.follower_id == follower.id
        assert subscription.blogger_id == blogger.id

    @pytest.mark.anyio
    async def test_double_subscribe(self, user, get_data):
        follower, blogger = get_data

        subscription_data = {
            "follower_id": follower.id,
            "blogger_id": blogger.id,
        }

        await SubscriptionDAO.add(**subscription_data)
        with pytest.raises(ReSubscriptionError):
            await SubscriptionDAO.add(**subscription_data)

    @pytest.mark.anyio
    async def test_subscribe_for_yourself(self, user, get_data):
        follower, _ = get_data

        subscription_data = {
            "follower_id": follower.id,
            "blogger_id": follower.id,
        }

        with pytest.raises(SubscriptionForYourselfError):
            await SubscriptionDAO.add(**subscription_data)
