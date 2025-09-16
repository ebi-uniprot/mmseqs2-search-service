from typing import TypedDict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from loguru import logger

from api.handlers.broker import BlockingQueueConnection
from api.handlers.db import MetaDataDb
from api.models.db import MetadataDbGetRequest, MetadataDbPostRequest
from api.models.fasta_input import FastaBlobModel
from api.status import TaskStatus


class StatusResponse(TypedDict):
    status: str
    uuid: str


def router(self, client: AsyncClient, db: MetaDataDb, queue: BlockingQueueConnection) -> APIRouter:
    router = APIRouter(tags=["status"])

    @router.post("/submit")
    async def submit(content: FastaBlobModel) -> JSONResponse:
        # When the model fails to validate FastaBlobModel the fastapi
        # will automatically send the response 422 Unprocessable Entity.
        logger.debug("New job: {}", content.job_id)

        msg = content.to_message()
        logger.debug("Publishing msg to queue: {}", content.job_id)
        with queue as q:
            result = q.publish_message(msg)
            match result:
                case TaskStatus.FAILED:
                    raise HTTPException(status_code=400, detail="Failed to upload task to the queue")

        logger.info("Publishing to database")

        # Database handling
        resp = await db.submit_job(MetadataDbPostRequest(job_id=content.job_id))
        # Always return 200, even if the actual status of the job is FAILED
        return JSONResponse(content=resp.model_dump(), status_code=200)

    @router.get("/status/{job_id}")
    async def status(job_id: str) -> JSONResponse:
        logger.info(f"Got GET request with {job_id}")
        resp = await db.get_job(data=MetadataDbGetRequest(job_id=job_id))
        return JSONResponse(content=resp.model_dump(), status_code=200)

    @router.get("/")
    async def healthcheck():
        return {"status": "ok"}

    return router
