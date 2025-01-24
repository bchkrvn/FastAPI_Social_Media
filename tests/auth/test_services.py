import base64
import json

import pytest
from fastapi import HTTPException, Request
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED

from application.auth.constants import COOKIES_TOKEN_KEY, TOKEN_EXPIRED_KEY, USER_ID_KEY
from application.auth.depends import get_token
from application.auth.messages import TOKEN_NOT_FOUND
from application.auth.schemas import SchemaLogin
from application.auth.services import auth_user, create_access_token, decode_access_token
from application.config import settings


class TestCreateAccessToken:
    @pytest.mark.anyio
    async def test_success(self, user, drop_user_table):
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
    async def test_success(self, user, password, drop_user_table):
        user_data = SchemaLogin(email=user.email, password=password)
        define_user = await auth_user(user_data)
        assert define_user.id == user.id

    @pytest.mark.anyio
    async def test_wrong_email(self, password, user, drop_user_table):
        wrong_email = "wrong@wrong.wrong"
        user_data = SchemaLogin(email=wrong_email, password=password)
        define_user = await auth_user(user_data)
        assert define_user is None

    @pytest.mark.anyio
    async def test_wrong_password(self, user, password, drop_user_table):
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


class TestDecodeAccessToken:
    def test_success(self):
        data = {"a": "1234"}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        decoded_data = decode_access_token(token)
        assert decoded_data == data

    def test_error(self):
        data = {"a": "1234"}
        token = jwt.encode(data, "a", algorithm=settings.ALGORITHM)
        with pytest.raises(JWTError):
            decode_access_token(token)
