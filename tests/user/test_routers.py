import datetime

import pytest
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from application.auth.constants import COOKIES_TOKEN_KEY
from application.auth.messages import TOKEN_NOT_FOUND
from application.user.dao import UserDAO
from application.user.messages import PASSWORD_NOT_VALID, SUCCESS_PASSWORD_CHANGE
from application.user.password import verify_password


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
            "followers_count": 0,
            "subscriptions_count": 0,
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
        updated_user = await UserDAO.find_one_or_none(filters=dict(id=user.id))
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
        deleted_user = await UserDAO.find_one_or_none(filters=dict(id=user.id))
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


class TestChangePasswordRouter:
    url = "/users/me/change_password"

    @pytest.mark.anyio
    async def test_change_password_200(self, auth_client, user, password):
        new_password = "Aa12345@"
        data = {
            "old_password": password,
            "password": new_password,
            "password2": new_password,
        }
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": SUCCESS_PASSWORD_CHANGE}

        updated_user = await UserDAO.find_one_or_none(filters=dict(id=user.id))
        assert verify_password(new_password, updated_user.password)

    @pytest.mark.anyio
    async def test_change_password_401_without_token(self, client, password):
        data = {
            "old_password": password,
            "password": "Aa12345@",
            "password2": "Aa12345@",
        }
        response = await client.post(self.url, json=data)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_change_password_409(self, auth_client, password):
        data = {
            "old_password": "Aa12345#",
            "password": "Aa12345@",
            "password2": "Aa12345@",
        }
        response_with_wrong_old_pwd = await auth_client.post(self.url, json=data)
        assert response_with_wrong_old_pwd.status_code == HTTP_409_CONFLICT
        assert response_with_wrong_old_pwd.json() == {"detail": PASSWORD_NOT_VALID}

    @pytest.mark.anyio
    async def test_change_password_422_data(self, auth_client, password):
        data = {
            "wrong_1": password,
            "wrong_2": "Aa12345@",
            "wrong_3": "Aa12345@",
        }
        response_with_empty_data = await auth_client.post(self.url)
        assert response_with_empty_data.status_code == HTTP_422_UNPROCESSABLE_ENTITY

        response_with_wrong_keys = await auth_client.post(self.url, json=data)
        assert response_with_wrong_keys.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_change_password_422_password(self, auth_client, password):
        data = {
            "old_password": password,
            "password": "!",
            "password2": "!",
        }
        response_with_simple_password = await auth_client.post(self.url, json=data)
        assert response_with_simple_password.status_code == HTTP_422_UNPROCESSABLE_ENTITY

        data = {
            "old_password": password,
            "password": "Aa12345@",
            "password2": "Aa12345%",
        }
        response_with_different_password = await auth_client.post(self.url, json=data)
        assert response_with_different_password.status_code == HTTP_422_UNPROCESSABLE_ENTITY
