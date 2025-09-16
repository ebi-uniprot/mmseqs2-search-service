from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from api.handlers.db import MetaDataDb
from api.models.db import MetadataDbGetRequest, MetaDataDbGetResponse, MetadataDbPostRequest, MetaDataDbPostResponse
from api.status import TaskStatus


@pytest.fixture
def endpoint():
    """Mock database endpoint."""
    return "http://mocked-db/"


@pytest.fixture
def job_id():
    """Mock job ID."""
    return "test-job-123"


class TestMetaDataDb:
    """Test class for MetaDataDb handler."""

    def _setup_mock_response(self, m_async_client: AsyncMock, method: str, status_code: int, json_data=None):
        """Helper to setup mock response for AsyncClient methods."""
        mock_client = m_async_client.return_value
        mock_response = MagicMock()
        mock_response.status_code = status_code
        if json_data is not None:
            mock_response.json.return_value = json_data
        getattr(mock_client.__aenter__.return_value, method).return_value = mock_response
        return mock_client

    def _assert_http_exception(self, exc, status_code: int, detail_substr: str):
        """Helper to assert HTTPException details."""
        assert str(status_code) in str(exc.value)
        assert exc.value.status_code == status_code
        assert detail_substr in str(exc.value.detail)

    @pytest.mark.asyncio
    @patch("api.handlers.db.AsyncClient")
    async def test_get_job_not_found(self, m_async_client: AsyncMock, endpoint: str, job_id: str):
        """Test get method returns 404 response and proper details."""
        # Patch the context manager's get method to return a real Response
        self._setup_mock_response(m_async_client, "get", 404)
        db = MetaDataDb(endpoint, m_async_client.return_value)
        data = MetadataDbGetRequest(job_id=job_id)
        with pytest.raises(HTTPException) as exc:
            await db.get_job(data)
        self._assert_http_exception(exc, 404, f"Failed to fetch {job_id} from database.")

    @pytest.mark.asyncio
    @patch("api.handlers.db.AsyncClient")
    async def test_get_job_unexpected_error(self, m_async_client: AsyncMock, endpoint: str, job_id: str):
        """Test get method returns 500 response and proper details."""
        self._setup_mock_response(m_async_client, "get", 500)
        db = MetaDataDb(endpoint, m_async_client.return_value)
        data = MetadataDbGetRequest(job_id=job_id)
        with pytest.raises(HTTPException) as exc:
            await db.get_job(data)
        self._assert_http_exception(exc, 500, f"Unexpected error while fetching job status for {job_id}.")

    @pytest.mark.asyncio
    @patch("api.handlers.db.AsyncClient")
    async def test_get_job_found(self, m_async_client: AsyncMock, endpoint: str, job_id: str):
        """Test get method returns 200 response with a json body."""
        resp_obj = MetaDataDbGetResponse(job_id=job_id, status=TaskStatus.FINISHED)
        self._setup_mock_response(m_async_client, "get", 200, resp_obj.model_dump())
        db = MetaDataDb(endpoint, m_async_client.return_value)
        data = MetadataDbGetRequest(job_id=job_id)
        result = await db.get_job(data)
        assert isinstance(result, MetaDataDbGetResponse)
        assert result.job_id == job_id
        assert result.status == TaskStatus.FINISHED

    @pytest.mark.asyncio
    @patch("api.handlers.db.AsyncClient")
    async def test_post_job_success(self, m_async_client: AsyncMock, endpoint: str, job_id: str):
        """Test post method returns 200 response with a json body."""
        resp_obj = MetaDataDbPostResponse(job_id=job_id, status=TaskStatus.QUEUED).model_dump()
        self._setup_mock_response(m_async_client, "post", 200, resp_obj)
        db = MetaDataDb(endpoint, m_async_client.return_value)
        data = MetadataDbPostRequest(job_id=job_id)
        resp = await db.post_job(data)
        assert resp.job_id == job_id
        assert resp.status == TaskStatus.QUEUED
        assert isinstance(resp, MetaDataDbPostResponse)

    @pytest.mark.asyncio
    @patch("api.handlers.db.AsyncClient")
    async def test_post_job_unexpected_error(self, m_async_client: AsyncMock, endpoint: str, job_id: str):
        """Test post method returns 500 response and proper details."""
        self._setup_mock_response(m_async_client, "post", 500)
        db = MetaDataDb(endpoint, m_async_client.return_value)
        data = MetadataDbPostRequest(job_id=job_id)
        with pytest.raises(HTTPException) as exc:
            await db.post_job(data)
        self._assert_http_exception(exc, 500, f"Unexpected error while posting job {job_id}.")
