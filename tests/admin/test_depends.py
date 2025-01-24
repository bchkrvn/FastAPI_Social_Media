import pytest
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from application.admin.depends import get_current_admin
from application.admin.messages import NOT_ADMIN


class TestGetCurrentAdmin:
    @pytest.mark.anyio
    async def test_success(self, admin):
        current_admin = await get_current_admin(admin)
        assert current_admin.id == admin.id

    @pytest.mark.anyio
    async def test_error(self, user):
        with pytest.raises(HTTPException) as ex:
            await get_current_admin(user)

        assert ex.value.status_code == HTTP_403_FORBIDDEN
        assert ex.value.detail == NOT_ADMIN
