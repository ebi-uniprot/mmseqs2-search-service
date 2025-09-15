from typing import Annotated

import pika
from fastapi import APIRouter

from api.models import FastaBlobModel

router = APIRouter(tags=["status"])
from loguru import logger


@router.post("/submit")
async def submit(fasta_content: FastaBlobModel) -> dict:
    logger.info("Received fasta content of size: {}", len(fasta_content))

    return {"status": "ok", "uuid": fasta_content.uuid}


@router.get("/status/{uuid}")
async def status() -> dict:
    return {"status": "ok"}


@router.get("/results/{uuid}")
async def results(uuid: str) -> dict:
    return {"status": "ok", "uuid": uuid}


@router.get("/")
async def healthcheck():
    return {"status": "ok"}
