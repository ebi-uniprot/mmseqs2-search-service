import pika
from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.post("/submit/")
async def submit() -> dict:
    return {"status": "ok"}


@router.get("/status/{uuid}")
async def status() -> dict:
    return {"status": "ok"}


@router.get("/results/{uuid}")
async def results(uuid: str) -> dict:
    return {"status": "ok", "uuid": uuid}


@router.get("/")
async def healthcheck():
    return {"status": "ok"}
