import pytest
from starlette.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from application.admin.messages import NOT_ADMIN
from application.config import settings
from application.post.dao import PostDAO
from application.post.messages import POST_DELETED, POST_NOT_FOUND
from application.post.model import Post


class TestGetAllPostsAdmin:
    url = "/admin/posts/"
    first_page_count = settings.PAGE_LIMIT
    second_page_count = 2

    @pytest.fixture
    async def prepare_data(self, session, drop_user_table, user):
        posts = []
        for i in range(self.first_page_count + self.second_page_count):
            data = {
                "text": f"text_{i}",
                "user_id": user.id,
            }
            post = Post(**data)
            posts.append(post)
            session.add(post)

        await session.commit()
        return posts

    async def get_expected_data(self, page):
        posts = await PostDAO.find_all(page=page)
        result = [
            {
                "id": p.id,
                "text": p.text,
                "created": p.created.isoformat(),
                "updated": p.updated.isoformat(),
                "user": {
                    "id": p.user.id,
                    "first_name": p.user.first_name,
                    "last_name": p.user.last_name,
                },
            }
            for p in posts
        ]
        return result

    @pytest.mark.anyio
    async def test_all_posts_200_first_page(self, auth_admin_client, prepare_data, user):
        PAGE = 1
        response_without_page = await auth_admin_client.get(self.url)
        response_with_page = await auth_admin_client.get(self.url, params={"page": PAGE})

        for r in (response_with_page, response_without_page):
            assert r.status_code == HTTP_200_OK
            items = await self.get_expected_data(page=PAGE)
            assert r.json() == {"page": 1, "count": self.first_page_count, "items": items[: self.first_page_count]}

    @pytest.mark.anyio
    async def test_all_posts_200_last_page(self, auth_admin_client, prepare_data):
        PAGE = 2
        response = await auth_admin_client.get(self.url, params={"page": PAGE})

        assert response.status_code == HTTP_200_OK
        items = await self.get_expected_data(page=PAGE)
        start = -self.second_page_count
        assert response.json() == {
            "page": PAGE,
            "count": self.second_page_count,
            "items": items[start:],
        }

    @pytest.mark.anyio
    async def test_all_users_403(self, auth_client, prepare_data):
        response = await auth_client.get(self.url)

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": NOT_ADMIN}

    @pytest.mark.anyio
    async def test_all_users_422(self, auth_admin_client, prepare_data):
        response = await auth_admin_client.get(self.url, params={"page": -1})

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestGetPostByIdAdmin:
    url = "/admin/posts/"

    @pytest.fixture
    async def create_post(self, session, user):
        data = {
            "text": "test",
            "user_id": user.id,
        }
        post = Post(**data)
        session.add(post)

        await session.commit()
        return post

    @pytest.mark.anyio
    async def test_200(self, auth_admin_client, user, create_post):
        post = await PostDAO.find_one_or_none(filters=dict(user_id=user.id))
        response = await auth_admin_client.get(self.url + str(post.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == {
            "id": post.id,
            "text": post.text,
            "created": post.created.isoformat(),
            "updated": post.updated.isoformat(),
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
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
        assert response.json() == {"detail": POST_NOT_FOUND}


class TestDeletePostByIdAdmin:
    url = "/admin/posts/"

    @pytest.fixture
    async def create_post(self, session, user):
        data = {
            "text": "test",
            "user_id": user.id,
        }
        post = Post(**data)
        session.add(post)

        await session.commit()
        return post

    @pytest.mark.anyio
    async def test_200(self, auth_admin_client, user, create_post):
        post = await PostDAO.find_one_or_none(filters=dict(user_id=user.id))
        response = await auth_admin_client.delete(self.url + str(post.id))

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": POST_DELETED}
        is_deleted = not await PostDAO.find_one_or_none(filters=dict(id=post.id))
        assert is_deleted

    @pytest.mark.anyio
    async def test_get_user_403(self, auth_client, user):
        response = await auth_client.delete(self.url + str(user.id))

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json() == {"detail": NOT_ADMIN}

    @pytest.mark.anyio
    async def test_get_user_404(self, auth_admin_client):
        response = await auth_admin_client.delete(self.url + "999999999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {"detail": POST_NOT_FOUND}
