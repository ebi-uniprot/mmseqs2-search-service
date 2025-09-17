"""Test controllers."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from loguru import logger

from api import App


@pytest.fixture(autouse=True, scope="session")
def disable_loguru_logs_for_testing(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Disable loguru logs for tests."""
    if "enable_loguru" in request.keywords:
        # Don't silence loguru if test is marked with @pytest.mark.enable_loguru
        yield
    else:
        logger.remove()
        yield
        logger.add(lambda _: None)


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
        mmseqs2_output_path=str(static_files),
        db_endpoint="localhost",
        db_port=8085,
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
