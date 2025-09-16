"""Test db models."""

import json
from pathlib import Path

import pytest

from api.models.db import MetadataDbGetRequest, MetaDataDbGetResponse, MetadataDbPostRequest, MetaDataDbPostResponse
from api.status import TaskStatus


def test_metadata_db_get_request():
    """Test MetadataDbGetRequest model."""
    req = MetadataDbGetRequest(job_id="1234")
    assert isinstance(req, MetadataDbGetRequest)
    assert req.job_id == "1234"


@pytest.mark.parametrize(
    "status",
    [
        pytest.param(TaskStatus.QUEUED, id="QUEUED"),
        pytest.param(TaskStatus.RUNNING, id="RUNNING"),
        pytest.param(TaskStatus.FINISHED, id="FINISHED"),
        pytest.param(TaskStatus.FAILED, id="FAILED"),
    ],
)
def test_metadata_db_get_response(status: TaskStatus):
    """Test MetadataDbGetResponse model."""
    resp = MetaDataDbGetResponse(job_id="1234", status=status)
    assert isinstance(resp, MetaDataDbGetResponse)
    assert resp.job_id == "1234"
    assert resp.status == status


@pytest.mark.parametrize(
    "mock_file",
    [
        pytest.param("db_get_queued_job.json", id="QUEUED"),
        pytest.param("db_get_running_job.json", id="RUNNING"),
        pytest.param("db_get_finished_job.json", id="FINISHED"),
        pytest.param("db_get_failed_job.json", id="FAILED"),
    ],
)
def test_metadata_db_post_response_with_mock(mocks: Path, mock_file: str) -> None:
    mock = mocks / mock_file
    assert mock.exists(), f"Mock file does not exist: {mock_file}"
    assert mock.is_file(), f"Mock file is not a file: {mock_file}"
    with open(mock) as f:
        data = json.load(f)
    resp = MetaDataDbPostResponse(**data)
    assert isinstance(resp, MetaDataDbPostResponse)
    assert resp.job_id == data["job_id"]
    assert resp.status == data["status"]
    assert resp.status in TaskStatus.__members__.values()


def test_metadata_db_post_request():
    """Test MetadataDbPostRequest model."""
    req = MetadataDbPostRequest(job_id="1234")
    assert isinstance(req, MetadataDbPostRequest)
    assert req.job_id == "1234"


@pytest.mark.parametrize(
    "status",
    [
        pytest.param(TaskStatus.QUEUED, id="QUEUED"),
        pytest.param(TaskStatus.RUNNING, id="RUNNING"),
        pytest.param(TaskStatus.FINISHED, id="FINISHED"),
        pytest.param(TaskStatus.FAILED, id="FAILED"),
    ],
)
def test_metadata_db_post_response(status: TaskStatus):
    """Test MetadataDbPostResponse model."""
    resp = MetaDataDbPostResponse(job_id="1234", status=status)
    assert isinstance(resp, MetaDataDbPostResponse)
    assert resp.job_id == "1234"
    assert resp.status == status
