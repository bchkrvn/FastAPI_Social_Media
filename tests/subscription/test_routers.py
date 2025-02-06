import pytest
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from application.auth.messages import TOKEN_NOT_FOUND
from application.subscription.dao import SubscriptionDAO
from application.subscription.messages import (
    BLOGGER_NOT_FOUND_ERROR,
    RE_SUBSCRIBE_ERROR,
    SUBSCRIBE_FOR_YOURSELF_ERROR,
    SUBSCRIPTION_NOT_FOUND,
    SUCCESS_SUBSCRIBE,
    SUCCESS_UNSUBSCRIBE,
)


class TestCreateSubscription:
    url = "/subscriptions/"

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, user_2, drop_subscription_table):
        data = {"blogger_id": user_2.id}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": SUCCESS_SUBSCRIBE}

    @pytest.mark.anyio
    async def test_401(self, client, user, user_2):
        data = {"blogger_id": user_2.id}
        response = await client.post(self.url, json=data)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_404_not_found_blogger(self, auth_client, user):
        data = {"blogger_id": 999999}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": BLOGGER_NOT_FOUND_ERROR}

    @pytest.mark.anyio
    async def test_409_subscribe_for_yourself(self, auth_client, user):
        data = {"blogger_id": user.id}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {"detail": SUBSCRIBE_FOR_YOURSELF_ERROR}

    @pytest.mark.anyio
    async def test_409_resubscribe(self, auth_client, user, user_2, drop_subscription_table):
        data = {"blogger_id": user_2.id}

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
