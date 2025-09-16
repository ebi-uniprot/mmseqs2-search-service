"""Routers for the API endpoints."""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.handlers.broker import BlockingQueueConnection
from api.handlers.db import MetaDataDb
from api.models.db import MetadataDbGetRequest, MetaDataDbGetResponse, MetadataDbPostRequest, MetaDataDbPostResponse
from api.models.fasta_input import FastaBlobModel


def router(db: MetaDataDb, queue: BlockingQueueConnection) -> APIRouter:
    """Router for the database and queue endpoints.

    This function creates an APIRouter with two endpoints:
    - POST /submit: Submits a fasta blob to the service.
    - GET /status/{job_id}: Gets the status of a job by its job_id.

    Args:
        db (MetaDataDb): The metadata database handler.
        queue (BlockingQueueConnection): The message queue handler.

    Returns:
        APIRouter: The configured API router.
    """
    router = APIRouter(tags=["status"])

    @router.post("/submit", response_model=MetaDataDbPostResponse, status_code=200)
    async def submit(content: FastaBlobModel) -> MetaDataDbPostResponse:
        """Submit a fasta blob to the service.

        This function is handler for the /submit endpoint.
        It checks if the job already exists in the metadata database.
        * If it does not exist, it publishes the job to the message queue and adds it to the database.
        * If the job already exists, it returns the existing job status.
        * If there is an unexpected error while fetching the job from the database, it raises a HTTPException with status code 500.

        Args:
            content (FastaBlobModel): The fasta blob and job_id to be submitted.

        Returns:
            MetaDataDbPostResponse: The response object containing job_id and status.

        Raises:
            HTTPException: If there is an unexpected error while fetching the job from the database (500).

        Note:
            When the model fails to validate FastaBlobModel the fastapi will automatically send the response 422 Unprocessable Entity.
        """
        logger.info("Got POST request")
        logger.debug(f"Fasta content: {content.fasta[:30]}...")
        logger.info(f"Job ID: {content.job_id}")

        logger.info(f"Checking if job {content.job_id} exists in database")
        initial_resp = await db.get_job_response(MetadataDbGetRequest(job_id=content.job_id))
        match initial_resp.status_code:
            case 404:
                logger.info(f"Job {content.job_id} not found in the database, submitting new job.")
                msg = content.to_message()
                logger.info(f"Publishing job {content.job_id} to queue.")
                queue.publish_message(msg)
                logger.success(f"Successfully published job {content.job_id} to queue.")
                logger.info(f"Publishing job {content.job_id} to database")
                resp = await db.post_job(MetadataDbPostRequest(job_id=content.job_id))
                logger.success(f"Successfully published job {content.job_id} to database.")
                logger.success(f"Successfully submitted job {content.job_id}")
                return resp
            case 200:
                logger.info(f"Job {content.job_id} found in the database, returning existing status.")
                resp_obj = MetaDataDbGetResponse(**initial_resp.json())
                logger.success(f"Job {content.job_id} status: {resp_obj.status}")
                return MetaDataDbPostResponse(job_id=resp_obj.job_id, status=resp_obj.status)
            case _:
                logger.error(f"Unexpected error while fetching job {content.job_id} from database.")
                raise HTTPException(status_code=500, detail=f"Failed fetching {content.job_id} from database.")

    @router.get("/status/{job_id}", response_model=MetaDataDbGetResponse, status_code=200)
    async def status(job_id: str) -> MetaDataDbGetResponse:
        """Get the status of a job by its job_id.

        This function is handler for the /status/{job_id} endpoint.
        It fetches the job status from the metadata database using the provided job_id.

        Args:
            job_id (str): The unique identifier for the job.

        Returns:
            MetaDataDbGetResponse: The response object containing job status and timestamps.

        Raises:
            HTTPException: If the job is not found (404) or if there is an unexpected error (500).
        """
        logger.info(f"Got GET request with {job_id}")
        res = await db.get_job(data=MetadataDbGetRequest(job_id=job_id))
        logger.success(f"Successfully fetched job {job_id} status: {res.status}")
        return res

    return router
