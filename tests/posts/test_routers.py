from unittest.mock import patch

import pytest
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from application.auth.messages import TOKEN_NOT_FOUND
from application.post.dao import PostDAO
from application.post.messages import POST_DELETED, POST_NOT_AUTHOR, POST_NOT_FOUND, POST_TIMEOUT
from application.post.model import Post
from application.user.model import User


class Base:
    count = 5

    def get_publication_data(self, publication: Post, user: User) -> dict:
        data = {
            "id": publication.id,
            "text": publication.text,
            "created": publication.created.isoformat(),
            "updated": publication.updated.isoformat(),
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
        return data

    async def create_post(self, user):
        await PostDAO.add(text="test", user_id=user.id)
        return await PostDAO.find_one_or_none(filters={"text": "test"})


class TestPostCreateRouter(Base):
    url = "/posts/"

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, drop_post_table):
        data = {"text": "test"}
        response = await auth_client.post(self.url, json=data)

        assert response.status_code == HTTP_200_OK
        publication = await PostDAO.find_one_or_none(filters={"text": "test"})
        assert publication
        assert publication.text == data["text"]

        assert response.json() == self.get_publication_data(publication, user)

    @pytest.mark.anyio
    async def test_401(self, client):
        data = {"text": "test"}
        response = await client.post(self.url, json=data)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_422(self, auth_client):
        response = await auth_client.post(self.url)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestGetPostsRouter(Base):
    url = "/posts/"
    count = 5

    @pytest.fixture
    async def create_posts(self, user, drop_post_table):
        for i in range(self.count):
            await PostDAO.add(text=f"test_{i}", user_id=user.id)

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, create_posts):
        response = await auth_client.get(self.url)

        assert response.status_code == HTTP_200_OK
        publications = await PostDAO.find_all()
        items = [self.get_publication_data(p, user) for p in publications]

        assert response.json() == {
            "count": self.count,
            "page": 1,
            "items": items,
        }

    @pytest.mark.anyio
    async def test_401(self, client):
        response = await client.get(self.url)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}


class TestGetPostRouter(Base):
    url = "/posts/"

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, drop_post_table):
        post = await self.create_post(user)

        response = await auth_client.get(self.url + str(post.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == self.get_publication_data(post, user)

    @pytest.mark.anyio
    async def test_200_another_author(self, auth_client, admin, drop_post_table):
        post = await self.create_post(admin)

        response = await auth_client.get(self.url + str(post.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == self.get_publication_data(post, admin)

    @pytest.mark.anyio
    async def test_401(self, client, user, drop_post_table):
        post = await self.create_post(user)

        response = await client.get(self.url + str(post.id))

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_404(self, auth_client):
        response = await auth_client.get(self.url + "99999999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": POST_NOT_FOUND}


class TestUpdatePostRouter(Base):
    url = "/posts/"
    data = {"text": "new"}

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, drop_post_table):
        post = await self.create_post(user)

        response = await auth_client.put(self.url + str(post.id), json=self.data)
        updated_post = await PostDAO.find_one_or_none(filters={"id": post.id})

        assert response.status_code == HTTP_200_OK
        assert response.json() == self.get_publication_data(updated_post, user)
        assert updated_post.text == self.data["text"]
        assert updated_post.updated > updated_post.created

    @pytest.mark.anyio
    async def test_401(self, client, user, drop_post_table):
        post = await self.create_post(user)

        response = await client.put(self.url + str(post.id))

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_403(self, auth_client, user, admin, drop_post_table):
        post = await self.create_post(admin)

        response = await auth_client.put(self.url + str(post.id), json=self.data)

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": POST_NOT_AUTHOR}

    @pytest.mark.anyio
    async def test_404(self, auth_client):
        response = await auth_client.put(self.url + "99999999", json=self.data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": POST_NOT_FOUND}

    @pytest.mark.anyio
    async def test_409(self, auth_client, user, drop_post_table):
        post = await self.create_post(user)

        with patch("application.post.model.POST_UPDATE_TIMEOUT", new=0.00001):
            response = await auth_client.put(self.url + str(post.id), json=self.data)

        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {"detail": POST_TIMEOUT}

    @pytest.mark.anyio
    async def test_422_data(self, auth_client, user, drop_post_table):
        post = await self.create_post(user)
        url = self.url + str(post.id)

        response_with_wrong_key = await auth_client.put(url, json={"wrong": "wrong"})
        response_with_wrong_type = await auth_client.put(url, json={"text": None})
        response_without_data = await auth_client.put(url)

        for r in (
            response_with_wrong_key,
            response_with_wrong_type,
            response_without_data,
        ):
            assert r.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_422_query(self, auth_client, user):
        response = await auth_client.put(self.url + "wrong", json=self.data)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestDeletePostRouter(Base):
    url = "/posts/"

    @pytest.mark.anyio
    async def test_200(self, auth_client, user, drop_post_table):
        post = await self.create_post(user)

        response = await auth_client.delete(self.url + str(post.id))
        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": POST_DELETED}

    @pytest.mark.anyio
    async def test_401(self, client, user, drop_post_table):
        post = await self.create_post(user)

        response = await client.delete(self.url + str(post.id))

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": TOKEN_NOT_FOUND}

    @pytest.mark.anyio
    async def test_403(self, auth_client, user, admin, drop_post_table):
        post = await self.create_post(admin)

        response = await auth_client.delete(self.url + str(post.id))

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": POST_NOT_AUTHOR}

    @pytest.mark.anyio
    async def test_404(self, auth_client):
        response = await auth_client.delete(self.url + "99999999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": POST_NOT_FOUND}
