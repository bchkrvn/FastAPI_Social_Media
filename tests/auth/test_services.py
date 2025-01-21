import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, Request
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from application.auth.exceptions import (
    EXPIRED_TOKEN,
    NOT_ADMIN,
    NOT_VALID_DATA,
    TOKEN_NOT_FOUND,
    TOKEN_NOT_VALID,
    USER_NOT_FOUND,
)
from application.auth.schemas import SchemaLogin
from application.auth.services import (
    COOKIES_TOKEN_KEY,
    TOKEN_EXPIRED_KEY,
    USER_ID_KEY,
    _decode_access_token,
    auth_user,
    create_access_token,
    get_current_admin,
    get_current_user,
    get_token,
)
from application.config import settings


class TestCreateAccessToken:
    @pytest.mark.anyio
    async def test_success(self, user):
        token = create_access_token(user)
        header, payload, _ = token.split(".")

        assert self.get_dict(header) == {"alg": "HS256", "typ": "JWT"}

        payload_dict = self.get_dict(payload)
        assert USER_ID_KEY in payload_dict
        assert payload_dict.get(USER_ID_KEY) == user.id
        assert TOKEN_EXPIRED_KEY in payload_dict
        assert isinstance(payload_dict[TOKEN_EXPIRED_KEY], int)

    def get_dict(self, data) -> dict:
        d = base64.standard_b64decode(data).decode("utf-8")
        data = json.loads(d)
        return data


class TestAuthUser:
    @pytest.mark.anyio
    async def test_success(self, user, password):
        user_data = SchemaLogin(email=user.email, password=password)
        define_user = await auth_user(user_data)
        assert define_user.id == user.id

    @pytest.mark.anyio
    async def test_wrong_email(self, password, user):
        wrong_email = "wrong@wrong.wrong"
        user_data = SchemaLogin(email=wrong_email, password=password)
        define_user = await auth_user(user_data)
        assert define_user is None

    @pytest.mark.anyio
    async def test_wrong_password(self, user, password):
        wrong_password = "12341234"
        user_data = SchemaLogin(email=user.email, password=wrong_password)
        define_user = await auth_user(user_data)
        assert define_user is None


class TestGetToken:
    def test_success(self):
        token = "1234"
        r = Request(scope={"type": "http"})
        r._cookies = {COOKIES_TOKEN_KEY: token}
        define_token = get_token(r)
        assert define_token == token

    def test_without_token(self):
        r = Request(scope={"type": "http"})
        r._cookies = {}
        with pytest.raises(HTTPException) as ex:
            get_token(r)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == TOKEN_NOT_FOUND


class TestGetCurrentUser:
    class FakeUser:
        def __init__(self, id_):
            self.id = id_

    def create_token(self, data) -> str:
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @pytest.mark.anyio
    async def test_success(self, user):
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
        assert ex.value.detail == NOT_VALID_DATA

    @pytest.mark.anyio
    async def test_token_has_not_user_id(self):
        data = {
            TOKEN_EXPIRED_KEY: datetime.now(timezone.utc),
        }
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == NOT_VALID_DATA

    @pytest.mark.anyio
    async def test_token_has_not_exp(self):
        data = {
            USER_ID_KEY: 1,
        }
        token = self.create_token(data)
        with pytest.raises(HTTPException) as ex:
            await get_current_user(token)

        assert ex.value.status_code == HTTP_401_UNAUTHORIZED
        assert ex.value.detail == NOT_VALID_DATA

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


class TestDecodeAccessToken:
    def test_success(self):
        data = {"a": "1234"}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        decoded_data = _decode_access_token(token)
        assert decoded_data == data

    def test_error(self):
        data = {"a": "1234"}
        token = jwt.encode(data, "a", algorithm=settings.ALGORITHM)
        with pytest.raises(JWTError):
            _decode_access_token(token)


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
