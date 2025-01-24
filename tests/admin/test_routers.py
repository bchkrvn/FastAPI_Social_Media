import datetime

import pytest
from starlette.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from application.admin.messages import NOT_ADMIN
from application.config import settings
from application.user.dao import UsersDAO
from application.user.messages import (
    SUCCESS_ACTIVATE,
    SUCCESS_DEACTIVATE,
    USER_ALREADY_ACTIVE,
    USER_ALREADY_DEACTIVE,
    USER_NOT_FOUND,
)
from application.user.model import User


class TestGetAllUsers:
    url = "/admin/all_users"
    first_page_count = settings.PAGE_LIMIT
    second_page_count = 2

    @pytest.fixture
    async def prepare_data(self, session, drop_user_table):
        # -1 т.к. еще есть учетная запись администратора
        for i in range(self.first_page_count + self.second_page_count - 1):
            data = {
                "email": f"test{i}@test.ru",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
            }
            user = User(**data)
            session.add(user)

        await session.commit()

    @pytest.mark.anyio
    async def test_all_users_200_first_page(self, auth_admin_client, prepare_data):
        response_without_page = await auth_admin_client.get(self.url)
        response_with_page = await auth_admin_client.get(self.url, params={"page": 1})

        for r in (response_with_page, response_without_page):
            assert r.status_code == HTTP_200_OK
            data = r.json()
            assert data.get("page") == 1
            assert data.get("count") == self.first_page_count
            assert "items" in data
            assert len(data["items"]) == self.first_page_count
            keys = {
                "id",
                "email",
                "first_name",
                "last_name",
                "date_of_birth",
                "is_active",
                "created",
                "updated",
            }
            assert set(data["items"][0]) == keys

    @pytest.mark.anyio
    async def test_all_users_200_last_page(self, auth_admin_client, prepare_data):
        response = await auth_admin_client.get(self.url, params={"page": 2})

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data.get("page") == 2
        assert data.get("count") == self.second_page_count
        assert "items" in data
        assert len(data["items"]) == self.second_page_count
        keys = {
            "id",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "is_active",
            "created",
            "updated",
        }
        assert set(data["items"][0]) == keys

    @pytest.mark.anyio
    async def test_all_users_403(self, auth_client, prepare_data):
        response = await auth_client.get(self.url)

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": NOT_ADMIN}

    @pytest.mark.anyio
    async def test_all_users_422(self, auth_admin_client, prepare_data):
        response = await auth_admin_client.get(self.url, params={"page": -1})

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestGetUserById:
    url = "/admin/users/"

    @pytest.mark.anyio
    async def test_get_user_200_first_page(self, auth_admin_client, user):
        response = await auth_admin_client.get(self.url + str(user.id))

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
    async def test_get_user_403(self, auth_client, user):
        response = await auth_client.get(self.url + str(user.id))

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": NOT_ADMIN}

    @pytest.mark.anyio
    async def test_get_user_404(self, auth_admin_client):
        response = await auth_admin_client.get(self.url + "999999999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": USER_NOT_FOUND}


class TestActivateUser:
    url = "/admin/users/{}/activate"

    @pytest.mark.anyio
    async def test_activate_200(self, auth_admin_client, user):
        await UsersDAO.deactivate(user)
        response = await auth_admin_client.get(self.url.format(user.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": SUCCESS_ACTIVATE}

    @pytest.mark.anyio
    async def test_get_user_403(self, auth_client, user):
        response = await auth_client.get(self.url.format(user.id))

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": NOT_ADMIN}

    @pytest.mark.anyio
    async def test_get_user_404(self, auth_admin_client):
        response = await auth_admin_client.get(self.url.format(9999999))

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": USER_NOT_FOUND}

    @pytest.mark.anyio
    async def test_get_user_409(self, auth_admin_client, user):
        response = await auth_admin_client.get(self.url.format(user.id))

        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {"detail": USER_ALREADY_ACTIVE}


class TestDeactivateUser:
    url = "/admin/users/{}/deactivate"

    @pytest.mark.anyio
    async def test_activate_200(self, auth_admin_client, user):
        response = await auth_admin_client.get(self.url.format(user.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": SUCCESS_DEACTIVATE}

    @pytest.mark.anyio
    async def test_get_user_403(self, auth_client, user):
        response = await auth_client.get(self.url.format(user.id))

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": NOT_ADMIN}

    @pytest.mark.anyio
    async def test_get_user_404(self, auth_admin_client):
        response = await auth_admin_client.get(self.url.format(9999999))

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": USER_NOT_FOUND}

    @pytest.mark.anyio
    async def test_get_user_409(self, auth_admin_client, user):
        await UsersDAO.deactivate(user)

        response = await auth_admin_client.get(self.url.format(user.id))

        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {"detail": USER_ALREADY_DEACTIVE}
