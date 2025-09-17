"""API endpoint tests."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Request, Response

from api.models.db import MetaDataDbPostResponse
from api.status import TaskStatus


class TestApi:
    """Test the API endpoints.

    Tests include:
    1. Submitting new fasta data (not in database).
    2. Submitting existing fasta data (already in database).
    3. Submitting invalid fasta data (empty sequence).
    4. Handling queue UnroutableError during submission. (expected to fail)
    5. Handling database POST error during submission.
    6. Getting status for non-existent job (404).
    7. Getting status for existing job.
    8. Handling database error during status check.
    9. Serving static files (non-existent file).
    10. Serving static files (existing file).
    """

    @pytest.mark.asyncio
    @patch("api.handlers.db.MetaDataDb.post_job", new_callable=AsyncMock)
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    @patch("api.handlers.broker.BlockingQueueConnection.publish_message", new_callable=MagicMock)
    async def test_submit_new_data(
        self,
        mock_publish: MagicMock,
        mock_get_job: MagicMock,
        mock_post_job: MagicMock,
        client: AsyncMock,
        valid_fasta: str,
        job_id: str,
    ):
        """User sends POST:/submit with the fasta blob and the data does not exist in the database.

        We expect
            * that the database returns 404 not found when checking for existing job
            * that the get_job_response is called once
            * that a new job is created in the database (post_job is called once)
            * that a new message is published to the queue (publish_message is called once)
            * that the response contains the job id
        """
        # Mock the response object to return 404 when running GET request.
        request = Request("GET", f"http://example.com/{job_id}")
        response_404 = Response(status_code=404, request=request)
        mock_get_job.return_value = response_404

        # Mock the post_job object to return the 200 and json object
        res = MetaDataDbPostResponse(job_id="123", status=TaskStatus.QUEUED)
        mock_post_job.return_value = res

        # Run the test
        response = client.post("/submit", json={"fasta": valid_fasta})
        assert response.status_code == 200
        mock_get_job.assert_called()
        mock_post_job.assert_called_once()
        mock_publish.assert_called_once()

    @pytest.mark.asyncio
    @patch("api.handlers.db.MetaDataDb.post_job", new_callable=AsyncMock)
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    @patch("api.handlers.broker.BlockingQueueConnection.publish_message", new_callable=MagicMock)
    async def test_submit_existing_data(
        self,
        mock_publish: MagicMock,
        mock_get_job: MagicMock,
        mock_post_job: MagicMock,
        client: AsyncMock,
        valid_fasta: str,
        job_id: str,
    ):
        """User sends POST:/submit with the fasta blob that already is in the database.

        We expect
            * that the database returns 200 with the job status
            * that the response contains the job id and status
            * that the get_job_response is called once
            * that no new job is created in the database (post_job is not called)
            * that no new message is published to the queue (publish_message is not called)

        """
        # Mock the response object to return 200 when running GET request.
        request = Request("GET", f"http://example.com/{job_id}")
        content = json.dumps({"job_id": job_id, "status": "RUNNING"})
        encoded = content.encode("utf-8")
        response_200 = Response(status_code=200, request=request, content=encoded)
        mock_get_job.return_value = response_200

        # Run the test
        response = client.post("/submit", json={"fasta": valid_fasta})

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == TaskStatus.RUNNING
        mock_get_job.assert_called_once()
        mock_post_job.assert_not_called()
        mock_publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_submit_invalid_fasta(self, client, invalid_fasta):
        """User sends POST:/submit with an invalid fasta blob (empty sequence)."""
        response = client.post("/submit", json={"fasta": invalid_fasta})
        assert response.status_code == 422
        assert "detail" in response.json()
        assert "Value error, Found empty fasta sequence." in response.text

    # 4. User submits the fasta blob and the queue raises UnroutableError
    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="UnroutableError error has to be handled securely, so the connection is closed properly.")
    @patch("api.handlers.db.MetaDataDb.post_job", new_callable=AsyncMock)
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    @patch("api.handlers.broker.BlockingQueueConnection.publish_message")
    async def test_submit_queue_unroutable(
        self, mock_publish, mock_get_job, mock_post_job, client, valid_fasta, job_id
    ):
        from api.handlers.broker import UnroutableError

        # Raise the UnroutableError when publishing the message to the queue
        mock_publish.side_effect = UnroutableError([])

        # Mock the response object to return 404 when running GET request.
        request = Request("GET", f"http://example.com/{job_id}")
        response_404 = Response(status_code=404, request=request)
        mock_get_job.return_value = response_404

        # Run the test
        response = client.post("/submit", json={"fasta": valid_fasta})
        assert response.status_code == 500
        assert "failed to publish message to queue" in response.text
        assert mock_publish.call_count == 1
        assert mock_get_job.call_count == 1
        assert mock_post_job.call_count == 0

    @pytest.mark.asyncio
    @patch("api.handlers.db.MetaDataDb.post_job", new_callable=AsyncMock)
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    @patch("api.handlers.broker.BlockingQueueConnection.publish_message")
    async def test_submit_db_post_error(self, mock_publish, mock_get_job, mock_post_job, client, valid_fasta, job_id):
        """User sends POST:/submit with the fasta blob and the database endpoint fails with error code other than 200.

        We expect
            * that the database returns 404 not found when checking for existing job
            * that the get_job_response is called once with 500 error
            * that no new job is created in the database (post_job is not called)
            * that no new message is published to the queue (publish_message is not called)
        """
        # Mock the response object to return 404 when running GET request.
        request = Request("GET", f"http://example.com/{job_id}")
        response_500 = Response(status_code=500, request=request)
        mock_get_job.return_value = response_500

        # get the job_id
        import hashlib

        job_id = hashlib.md5(valid_fasta.encode("utf-8")).hexdigest()

        # Run the test
        response = client.post("/submit", json={"fasta": valid_fasta})
        assert response.status_code == 500
        assert f"Failed fetching {job_id} from database." in response.text
        assert mock_publish.call_count == 0
        assert mock_get_job.call_count == 1
        assert mock_post_job.call_count == 0

    @pytest.mark.asyncio
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    async def test_status_not_found(self, mock_get_job, client, job_id):
        """User sends GET:/status/{job_id} and job_id is not found.

        We expect:
            * that the database returns 404 not found when checking for existing job
            * that the get_job_response is called once
            * that the response is 404 with job not found message
        """
        # Mock the get_job_response to raise HTTPException when job is not found
        request = Request("GET", f"http://example.com/{job_id}")
        response_404 = Response(status_code=404, request=request)
        mock_get_job.return_value = response_404

        # Run the test
        response = client.get(f"/status/{job_id}")
        assert response.status_code == 404
        assert f"Failed to fetch {job_id} from database." in response.text

    @pytest.mark.asyncio
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    async def test_status_found(self, mock_get_job, client, job_id):
        """User sends GET:/status/{job_id} and job_id is found.

        We expect:
            * that the database returns 200 with the job status
            * that the get_job_response is called once
            * that the response contains the job id and status
        """
        # Mock the response object to return 200 when running GET request.
        request = Request("GET", f"http://example.com/{job_id}")
        content = json.dumps({"job_id": job_id, "status": "RUNNING"})
        encoded = content.encode("utf-8")
        response_200 = Response(status_code=200, request=request, content=encoded)
        mock_get_job.return_value = response_200

        # Run the test
        response = client.get(f"/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == TaskStatus.RUNNING
        mock_get_job.assert_called_once()

    @pytest.mark.asyncio
    @patch("api.handlers.db.MetaDataDb.get_job_response", new_callable=AsyncMock)
    async def test_status_db_error(self, mock_get_job, client, job_id):
        """User sends GET:/status/{job_id} and the database returns an error.

        We expect:
            * that the database returns 500 when checking for existing job
            * that the get_job_response is called once
            * that the response is 500 with error message
        """
        # Mock the get_job_response to raise HTTPException when job is not found
        request = Request("GET", f"http://example.com/{job_id}")
        response_500 = Response(status_code=500, request=request)
        mock_get_job.return_value = response_500

        # Run the test
        response = client.get(f"/status/{job_id}")
        assert response.status_code == 500
        assert f"Unexpected error while fetching job status for {job_id}." in response.text
        mock_get_job.assert_called_once()

    def test_static_files_serving(self, client):
        """Test /results/{job_id} endpoint for non-existent file."""
        response = client.get("/results/non_existent_job_id")
        assert response.status_code == 404
        assert "Results for job non_existent_job_id not found." in response.text

    def test_static_files_serving_existing(self, client, static_files: Path):
        """Test /results/{job_id} endpoint for existing file."""
        static = static_files / "sequence.m8"
        assert static.exists(), f"Static file does not exist: {static}"
        assert static.is_file(), f"Static file is not a file: {static}"

        response = client.get("/results/sequence")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "some content" in response.text
