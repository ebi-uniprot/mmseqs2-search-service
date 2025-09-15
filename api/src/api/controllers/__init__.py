from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from api.models import FastaBlobModel

router = APIRouter(tags=["status"])
from httpx import Client
from loguru import logger


@router.post("/submit")
async def submit(fasta_content: FastaBlobModel) -> dict:
    logger.debug("Received fasta content of size: {}", len(fasta_content))
    logger.debug("Fasta UUID: {}", fasta_content.uuid)
    logger.debug("Message: {}", fasta_content.to_message())

    return {"status": "ok", "uuid": fasta_content.uuid}


@router.get("/status/{uuid}")
async def status(uuid: str) -> dict:
    c = Client()
    response = c.get(f"http://example.com/status/{uuid}")
    return {"status": "ok", "uuid": uuid}


@router.get("/")
async def healthcheck():
    return {"status": "ok"}
