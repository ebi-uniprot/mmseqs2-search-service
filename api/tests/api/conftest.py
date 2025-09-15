"""Test controllers."""

import pytest
from fastapi.testclient import TestClient

from api import App


@pytest.fixture
def client() -> TestClient:
    app = App().app
    return TestClient(app)
