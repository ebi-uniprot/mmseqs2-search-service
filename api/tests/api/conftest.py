"""Test controllers."""

from pathlib import Path
from unittest.mock import MagicMock

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
def static_files() -> Path:
    """Get the path to the static files."""
    p = Path(__file__).parent.parent / "data"
    assert p.exists(), f"Static files directory does not exist: {p}"
    assert p.is_dir(), f"Static files path is not a directory: {p}"
    return p


@pytest.fixture
def client(static_files: Path) -> TestClient:
    # Patch __enter__ to return a mock with publish_message as a MagicMock
    queue_mock = MagicMock()
    queue_mock.publish_message = MagicMock()
    app = App(
        fasta_output_path=str(static_files),
        db_endpoint="sqlite:///:memory:",
        queue_name="test-queue",
        queue_username="user",
        queue_passwd="pass",  # noqa: S106
        queue_port=5672,
        queue_host="localhost",
    ).app
    return TestClient(app)


@pytest.fixture
def valid_fasta():
    return ">seq1\nMKTAYIAKQRQISFVKSHFSRQDILDLWIYHTQGYFPQ\n"


@pytest.fixture
def invalid_fasta():
    return ">seq1\n\n"  # empty sequence


@pytest.fixture
def job_id():
    return "b6c7b6e2e2e2e2e2e2e2e2e2e2e2e2"
