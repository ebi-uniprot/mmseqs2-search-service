"""Db handlers."""

from urllib.parse import urljoin

from fastapi import HTTPException
from httpx import AsyncClient, Response

from api.models.db import MetadataDbGetRequest, MetaDataDbGetResponse, MetadataDbPostRequest, MetaDataDbPostResponse
from api.status import TaskStatus


class MetaDataDb:
    def __init__(self, endpoint: str, client: AsyncClient) -> None:
        self.client = client
        self.post_job_url = urljoin(endpoint, "job")
        self.get_job_status_url = urljoin(endpoint, "job")

    async def _post_job(self, data: MetadataDbPostRequest) -> MetaDataDbPostResponse:
        """Post job to the metadata database.

        The expected status codes are:
           - 200 when the job was successfully uploaded to the db (QUEUED response)
           - any other status code will trigger FAILURE response

        Args:
            data (MetadataDbPostRequest): The job submission data.

        Returns:
            MetaDataDbPostResponse: The job submission response.

        """
        async with self.client as c:
            resp = await c.post(url=self.post_job_url, data=data.model_dump())
            match resp.status_code:
                case 200:
                    return MetaDataDbPostResponse(job_id=data.job_id, status=TaskStatus.QUEUED)
                case _:
                    raise HTTPException(status_code=500, detail="Unexpected error")

    async def _get_job(self, data: MetadataDbGetRequest) -> Response:
        """Intermediate step reused to run the get request to the metadata db.

        Args:
            data (MetadataDbGetRequest): request object containing the job ID.

        Returns:
            Response: httpx response object
        """
        async with self.client as c:
            job_url = urljoin(self.get_job_status_url, data.job_id)
            return await c.get(url=job_url)

    async def get_job(self, data: MetadataDbGetRequest) -> MetaDataDbGetResponse:
        """Get the job status from the metadata database.

        This coroutine should be used with the /status/{uuid} endpoint.
        The status for the job can be any status that is defined in the database.

        Args:
            data (MetadataDbGetRequest): The request object containing the job ID.

        Raises:
            ValueError: If the job is not found or if the response format is invalid.


        Returns:
            MetaDataDbGetResponse: The job status response object.

        """
        resp = await self._get_job(data=data)
        match resp.status_code:
            case 200:
                return MetaDataDbGetResponse(**resp.json())
            case 404:
                raise HTTPException(status_code=404, detail=f"Job with {data.job_id} not submitted.")
            case _:
                raise HTTPException(status_code=500, detail="Unexpected error")

    async def submit_job(self, data: MetadataDbPostRequest) -> MetaDataDbPostResponse:
        """Submit a job to the metadata database.

        If the job already exists, it retrieves its status instead of creating a new entry.
        The status messages produced by the coroutine are:
            - QUEUED: Job was successfully queued in the database.
            - FAILED: Job submission failed or an error occurred during the process.
            - any other status from the existing job if it was already present in the database.

        Args:
            data (MetadataDbPostRequest): The job submission data.

        Returns:
            MetaDataDbPostResponse: The job submission response.
        """
        request_data = MetadataDbGetRequest(job_id=data.job_id)
        initial_resp = await self._get_job(data=request_data)
        match initial_resp.status_code:
            case 404:
                return await self._post_job(data)
            case 200:
                resp_obj = MetaDataDbGetResponse(**initial_resp.json())
                return MetaDataDbPostResponse(job_id=resp_obj.job_id, status=resp_obj.status)
            case _:
                raise HTTPException(status_code=500, detail="Unexpected error")
