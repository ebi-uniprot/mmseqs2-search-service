"""Database handlers."""

from urllib.parse import urljoin

from fastapi import HTTPException
from httpx import AsyncClient, Response
from loguru import logger

from api.models.db import MetadataDbGetRequest, MetaDataDbGetResponse, MetadataDbPostRequest, MetaDataDbPostResponse
from api.status import TaskStatus


class MetaDataDb:
    """Class to handle interactions with the metadata database."""

    def __init__(self, endpoint: str, client: AsyncClient) -> None:
        """Initialize the MetaDataDb handler.

        Args:
            endpoint (str): The metadata database endpoint.
            client (AsyncClient): The HTTPX async client to use for requests.
        """
        self.client = client
        self.post_job_url = urljoin(endpoint, "job/")
        self.get_job_status_url = urljoin(endpoint, "job")

    async def post_job(self, data: MetadataDbPostRequest) -> MetaDataDbPostResponse:
        """Post job to the metadata database.

        The expected status codes are:
           - 200 when the job was successfully uploaded to the db (QUEUED response)
           - any other status code will trigger FAILURE response

        Args:
            data (MetadataDbPostRequest): The job submission data.

        Returns:
            MetaDataDbPostResponse: The job submission response.

        Raises:
            HTTPException: If there is an unexpected error while posting the job (500).

        """
        logger.info(f"Data model dump {data.model_dump()}")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        resp = await self.client.post(url=self.post_job_url, json=data.model_dump(), headers=headers)
        match resp.status_code:
            case 200:
                return MetaDataDbPostResponse(job_id=data.job_id, status=TaskStatus.QUEUED)
            case _:
                raise HTTPException(status_code=500, detail=f"Unexpected error while posting job {data.job_id}.")

    async def get_job_response(self, data: MetadataDbGetRequest) -> Response:
        """Intermediate step reused to run the get request to the metadata db.

        This is part of the get_job coroutine and is utilized to get the raw HTTPX response
        for the /submit/{job_id} endpoint when we need to check if the job_id exists in the db,
        which is indicated by a 404 response.

        Args:
            data (MetadataDbGetRequest): request object containing the job ID.

        Returns:
            Response: httpx response object
        """
        logger.info(f"Fetching job {data.job_id} from database.")
        job_url = f"{self.get_job_status_url}/{data.job_id}"
        logger.info(f"Fetching job {job_url} from database.")
        return await self.client.get(url=job_url)

    async def get_job(self, data: MetadataDbGetRequest) -> MetaDataDbGetResponse:
        """Get the job status from the metadata database.

        This coroutine should be used with the /status/{job_id} endpoint.
        The status for the job can be any status that is defined in the database.

        Args:
            data (MetadataDbGetRequest): The request object containing the job ID.

        Raises:
            HTTPException: If the job is not found or if the response format is invalid.

        Returns:
            MetaDataDbGetResponse: The job status response object.

        """
        resp = await self.get_job_response(data=data)
        match resp.status_code:
            case 200:
                return MetaDataDbGetResponse(**resp.json())
            case 404:
                raise HTTPException(status_code=404, detail=f"Failed to fetch {data.job_id} from database.")
            case _:
                raise HTTPException(
                    status_code=500, detail=f"Unexpected error while fetching job status for {data.job_id}."
                )
