import datetime

import pytest
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from application.auth.messages import TOKEN_NOT_FOUND
from application.base.schemas import get_paginated_response
from application.config import settings
from application.subscription.dao import SubscriptionDAO
from application.subscription.messages import (
    BLOGGER_NOT_FOUND_ERROR,
    RE_SUBSCRIBE_ERROR,
    SUBSCRIBE_FOR_YOURSELF_ERROR,
    SUBSCRIPTION_NOT_FOUND,
    SUCCESS_SUBSCRIBE,
    SUCCESS_UNSUBSCRIBE,
)
from application.user.dao import UserDAO


class TestCreateSubscription:
    url = "/subscriptions/"

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, user_2, drop_subscription_table):
        data = {"user_id": user_2.id}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": SUCCESS_SUBSCRIBE}

    @pytest.mark.anyio
    async def test_401(self, client, user, user_2):
        data = {"user_id": user_2.id}
        response = await client.post(self.url, json=data)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_404_not_found_blogger(self, auth_client, user):
        data = {"user_id": 999999}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": BLOGGER_NOT_FOUND_ERROR}

    @pytest.mark.anyio
    async def test_409_subscribe_for_yourself(self, auth_client, user):
        data = {"user_id": user.id}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {"detail": SUBSCRIBE_FOR_YOURSELF_ERROR}

    @pytest.mark.anyio
    async def test_409_resubscribe(self, auth_client, user, user_2, drop_subscription_table):
        data = {"user_id": user_2.id}

        response = await auth_client.post(self.url, json=data)
        assert response.status_code == HTTP_200_OK

        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {"detail": RE_SUBSCRIBE_ERROR}


class TestDeleteSubscription:
    url = "/subscriptions/"

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, user_2, drop_subscription_table):
        data = {
            "blogger_id": user_2.id,
            "follower_id": user.id,
        }
        subscription = await SubscriptionDAO.add(**data)
        response = await auth_client.delete(self.url + str(subscription.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": SUCCESS_UNSUBSCRIBE}

        s = await SubscriptionDAO.find_one_or_none(filters=dict(id=subscription.id))
        assert s is None

    @pytest.mark.anyio
    async def test_401(self, client, user, user_2):
        data = {
            "blogger_id": user_2.id,
            "follower_id": user.id,
        }
        subscription = await SubscriptionDAO.add(**data)
        response = await client.delete(self.url + str(subscription.id))

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_404(self, auth_client):
        response = await auth_client.delete(self.url + "999999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": SUBSCRIPTION_NOT_FOUND}

    @pytest.mark.anyio
    async def test_404_another_user(self, auth_client, user, user_2):
        data = {
            "blogger_id": user.id,
            "follower_id": user_2.id,
        }
        subscription = await SubscriptionDAO.add(**data)
        response = await auth_client.delete(self.url + str(subscription.id))

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": SUBSCRIPTION_NOT_FOUND}


class BaseSubscriptions:
    second_page_count = 3
    url = None

    def get_expected_data(self, data: list) -> list:
        result = [
            {
                "id": s.id,
                "user": {
                    "id": u.id,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                },
            }
            for s, u in data
        ]
        return result

    @pytest.mark.anyio
    async def test_200_first_page(self, auth_client, user_2, prepare_data):
        page = 1
        params = {"user_id": user_2.id}
        params_with_page = {"user_id": user_2.id, "page": page}
        response = await auth_client.get(self.url, params=params)
        response_with_page = await auth_client.get(self.url, params=params_with_page)

        data = self.get_expected_data(prepare_data[: settings.PAGE_LIMIT])

        for r in (response, response_with_page):
            assert r.status_code == HTTP_200_OK
            assert r.json() == get_paginated_response(data, page)

    @pytest.mark.anyio
    async def test_200_last_page(self, auth_client, user_2, prepare_data):
        page = 2
        params_with_page = {"user_id": user_2.id, "page": page}
        response_with_page = await auth_client.get(self.url, params=params_with_page)

        s = -1 * self.second_page_count
        data = self.get_expected_data(prepare_data[s:])

        assert response_with_page.status_code == HTTP_200_OK
        assert response_with_page.json() == get_paginated_response(data, page)

    @pytest.mark.anyio
    async def test_401(self, client):
        response = await client.get(self.url)
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_422(self, auth_client):
        response = await auth_client.get(self.url)
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestGetUserSubscriptions(BaseSubscriptions):
    url = "/subscriptions/subscriptions"

    @pytest.fixture
    async def prepare_data(self, user_2, drop_subscription_table, drop_user_table):
        subscriptions = []
        for i in range(settings.PAGE_LIMIT + self.second_page_count):
            user_data = {
                "email": f"{i}@test.test",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
            }
            created_user = await UserDAO.add(**user_data)
            subscription = await SubscriptionDAO.add(blogger_id=created_user.id, follower_id=user_2.id)
            subscriptions.append((subscription, created_user))

        return subscriptions


class TestGetUserFollowers(BaseSubscriptions):
    url = "/subscriptions/followers"

    @pytest.fixture
    async def prepare_data(self, user_2, drop_subscription_table, drop_user_table):
        subscriptions = []
        for i in range(settings.PAGE_LIMIT + self.second_page_count):
            user_data = {
                "email": f"{i}@test.test",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
            }
            created_user = await UserDAO.add(**user_data)
            subscription = await SubscriptionDAO.add(follower_id=created_user.id, blogger_id=user_2.id)
            subscriptions.append((subscription, created_user))

        return subscriptions
