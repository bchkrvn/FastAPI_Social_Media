import pytest
from starlette.status import HTTP_200_OK


class TestPing:
    url = "/ping"

    @pytest.mark.anyio
    async def test_ping(self, client):
        response = await client.get(self.url)

        assert response.status_code == HTTP_200_OK
        assert response.json() == {"msg": "pong"}
