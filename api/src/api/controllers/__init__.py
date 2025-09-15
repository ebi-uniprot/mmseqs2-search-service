from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.post("/submit/")
def submit() -> dict:
    return {"status": "ok"}


@router.get("/status/{uuid}")
def status() -> dict:
    return {"status": "ok"}


@router.get("/results/{uuid}")
def results(uuid: str) -> dict:
    return {"status": "ok", "uuid": uuid}


@router.get("/")
def healthcheck():
    return {"status": "ok"}
