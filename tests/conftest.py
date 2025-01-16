import pytest
from fastapi.testclient import TestClient

from application.main import app


@pytest.fixture
def client():
    client = TestClient(app)
    return client
