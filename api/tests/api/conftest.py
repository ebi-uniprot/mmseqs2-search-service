"""Test controllers."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api import App


@pytest.fixture
def mocks() -> Path:
    """Get the path to the blob mocks."""
    p = Path(__file__).parent.parent.parent.parent / "mocks"
    assert p.exists(), f"Mocks directory does not exist: {p}"
    assert p.is_dir(), f"Mocks path is not a directory: {p}"
    return p


@pytest.fixture
def client() -> TestClient:
    app = App(
        fasta_output_path="/tmp/fasta",
        db_endpoint="sqlite:///:memory:",
        queue_name="test-queue",
        queue_username="user",
        queue_passwd="pass",
        queue_port=5672,
        queue_host="localhost",
    ).app
    return TestClient(app)
