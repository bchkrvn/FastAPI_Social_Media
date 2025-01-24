import pytest

from application.user.dao import UsersDAO


class TestUserDAO:
    @pytest.mark.anyio
    async def test_deactivate(self, user, session):
        await UsersDAO.deactivate(user)
        deleted_user = await UsersDAO.find_one_or_none(id=user.id)
        assert deleted_user.id == user.id
        assert not deleted_user.is_active
