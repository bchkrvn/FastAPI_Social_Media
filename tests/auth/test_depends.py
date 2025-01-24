from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt
from starlette.status import HTTP_401_UNAUTHORIZED

from application.auth.constants import TOKEN_EXPIRED_KEY, USER_ID_KEY
from application.auth.depends import get_current_user
from application.auth.messages import EXPIRED_TOKEN, NOT_VALID_TOKEN_DATA, TOKEN_NOT_VALID
from application.auth.services import create_access_token
from application.config import settings
from application.user.messages import USER_NOT_FOUND


class TestGetCurrentUser:
    class FakeUser:
        def __init__(self, id_):
            self.id = id_

    def create_token(self, data) -> str:
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @pytest.mark.anyio
    async def test_success(self, user, drop_user_table):
        token = create_access_token(user)
        current_user = await get_current_user(token)
        assert current_user.id == user.id

    @pytest.mark.anyio
    async def test_not_valid_token(self):
        token = jwt.encode({}, "a", algorithm=settings.ALGORITHM)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == TOKEN_NOT_VALID

    @pytest.mark.anyio
    async def test_token_has_not_data(self):
        data = {}
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == NOT_VALID_TOKEN_DATA

    @pytest.mark.anyio
    async def test_token_has_not_user_id(self):
        data = {
            TOKEN_EXPIRED_KEY: datetime.now(timezone.utc),
        }
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == NOT_VALID_TOKEN_DATA

    @pytest.mark.anyio
    async def test_token_has_not_exp(self):
        data = {
            USER_ID_KEY: 1,
        }
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == NOT_VALID_TOKEN_DATA

    @pytest.mark.anyio
    async def test_expired_token(self):
        data = {
            USER_ID_KEY: 1,
            TOKEN_EXPIRED_KEY: datetime.now(timezone.utc),
        }
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == EXPIRED_TOKEN

    @pytest.mark.anyio
    async def test_user_not_found(self):
        data = {
            USER_ID_KEY: 9999999,
            TOKEN_EXPIRED_KEY: datetime.now(timezone.utc) + timedelta(minutes=1),
        }
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == USER_NOT_FOUND
