import datetime

import pytest
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from application.auth.constants import COOKIES_TOKEN_KEY
from application.auth.messages import NOT_VALID_EMAIL_OR_PASSWORD, SUCCESS_REGISTRATION
from application.user.dao import UserDAO
from application.user.messages import NOT_UNIQUE_USER


class TestAuthRouterRegister:
    """Тестирование API создания пользователя"""

    url = "/auth/register"
    user_data = {
        "email": "test@test.ru",
        "password": "Aa12345@",
        "first_name": "test_name",
        "last_name": "test_lastname",
        "date_of_birth": "01.01.2025",
    }

    @pytest.mark.anyio
    async def test_register_user_200(self, client, drop_user_table):
        response = await client.post(self.url, json=self.user_data)

        assert response.status_code == HTTP_200_OK, response.json()
        assert response.json() == {"message": SUCCESS_REGISTRATION}

    @pytest.mark.anyio
    async def test_register_user_409(self, client, user):
        user_data = self.user_data.copy()
        user_data["date_of_birth"] = datetime.date(year=2025, day=1, month=1)
        user = await UserDAO.add(**user_data)

        response = await client.post(self.url, json=self.user_data)

        assert response.status_code == HTTP_409_CONFLICT, response.json()
        msg = NOT_UNIQUE_USER.format(user.email)
        assert response.json() == {"detail": msg}

    @pytest.mark.anyio
    async def test_register_user_422(self, client):
        response = await client.post(self.url, json={})

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY, response.json()


class TestAuthRouterLogin:
    """Тестирование API аутентификации"""

    url = "/auth/login"

    @pytest.mark.anyio
    async def test_login_200(self, client, user, password, drop_user_table):
        login_data = {
            "email": user.email,
            "password": password,
        }

        response = await client.post(self.url, json=login_data)

        assert response.status_code == HTTP_200_OK
        assert "access_token" in response.cookies
        assert "access_token" in response.json()
        assert response.cookies[COOKIES_TOKEN_KEY] == response.json()[COOKIES_TOKEN_KEY]

    @pytest.mark.anyio
    async def test_login_401_email(self, client, password):
        login_data = {
            "email": "wrong@test.test",
            "password": password,
        }

        response = await client.post(self.url, json=login_data)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": NOT_VALID_EMAIL_OR_PASSWORD}

    @pytest.mark.anyio
    async def test_login_401_password(self, client, user):
        login_data = {
            "email": user.email,
            "password": "12341234",
        }

        response = await client.post(self.url, json=login_data)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": NOT_VALID_EMAIL_OR_PASSWORD}

    @pytest.mark.anyio
    async def test_login_422(self, client, user):
        response = await client.post(self.url, json={})

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthRouterLogout:
    """Тестирование API выхода из системы"""

    url = "/auth/logout"

    @pytest.mark.anyio
    async def test_with_cookie(self, client):
        cookies = {COOKIES_TOKEN_KEY: "1234"}
        response = await client.get(self.url, cookies=cookies)

        assert response.status_code == HTTP_200_OK
        assert COOKIES_TOKEN_KEY not in response.cookies

    @pytest.mark.anyio
    async def test_without_cookie(self, client):
        response = await client.get(self.url)

        assert response.status_code == HTTP_200_OK
        assert COOKIES_TOKEN_KEY not in response.cookies
