import datetime

import pytest
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY

from application.auth.constants import COOKIES_TOKEN_KEY
from application.auth.messages import TOKEN_NOT_FOUND
from application.user.dao import UsersDAO


class TestMeGetRouter:
    url = "/users/me"

    @pytest.mark.anyio
    async def test_me_200(self, auth_client, user):
        response = await auth_client.get(self.url)

        assert response.status_code == HTTP_200_OK
        assert response.json() == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": str(user.date_of_birth),
            "is_active": user.is_active,
            "created": user.created.isoformat(),
            "updated": user.updated.isoformat(),
        }

    @pytest.mark.anyio
    async def test_me_401_without_token(self, client):
        response = await client.get(self.url)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": TOKEN_NOT_FOUND,
        }


class TestMePutRouter:
    url = "/users/me"

    @pytest.mark.anyio
    async def test_me_200(self, auth_client, user):
        date = datetime.date.today()
        str_date = date.strftime("%d.%m.%Y")
        data = {
            "email": "new@test.ru",
            "first_name": "new",
            "last_name": "new",
            "date_of_birth": str_date,
        }

        response = await auth_client.put(self.url, json=data)

        assert response.status_code == HTTP_200_OK, response.json()
        updated_user = await UsersDAO.find_one_or_none(filters=dict(id=user.id))
        assert response.json() == {
            "id": user.id,
            "email": data["email"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "date_of_birth": str(date),
            "is_active": updated_user.is_active,
            "created": updated_user.created.isoformat(),
            "updated": updated_user.updated.isoformat(),
        }

    @pytest.mark.anyio
    async def test_me_401_without_token(self, client):
        response = await client.put(self.url)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": TOKEN_NOT_FOUND,
        }

    @pytest.mark.anyio
    async def test_me_422_without_data(self, auth_client):
        response = await auth_client.put(self.url)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestMeDeleteRouter:
    url = "/users/me"

    @pytest.mark.anyio
    async def test_me_200(self, auth_client, user):
        response = await auth_client.delete(self.url)

        assert response.status_code == HTTP_200_OK, response.json()
        deleted_user = await UsersDAO.find_one_or_none(filters=dict(id=user.id))
        assert deleted_user.id == user.id
        assert not deleted_user.is_active
        assert COOKIES_TOKEN_KEY not in response.cookies

    @pytest.mark.anyio
    async def test_me_401_without_token(self, client):
        response = await client.delete(self.url)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": TOKEN_NOT_FOUND,
        }
