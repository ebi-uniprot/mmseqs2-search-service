from typing import Annotated

import pika
from fastapi import APIRouter

from api.models import FileModel

router = APIRouter(tags=["status"])
from fastapi import File
from loguru import logger


@router.post("/submit")
async def submit(file: Annotated[bytes, File(description="A file read as bytes")]) -> dict:
    logger.info("Received file of size: {} bytes", len(file))
    f = FileModel(file=file)

    # Generate the uuid
    return {"status": "ok", "uuid": f.uuid}


@router.get("/status/{uuid}")
async def status() -> dict:
    return {"status": "ok"}


@router.get("/results/{uuid}")
async def results(uuid: str) -> dict:
    return {"status": "ok", "uuid": uuid}


@router.get("/")
async def healthcheck():
    return {"status": "ok"}
