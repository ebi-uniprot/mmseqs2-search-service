import datetime
from typing import Union, Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine
from pydantic import BaseModel


class Job(SQLModel, table=True):
    job_id: str = Field(primary_key=True, index=True)
    status: str
    submitted_at: str
    completed_at: Union[str, None] = None
    # data: Union[object, None] = Field(default=None)


sqlite_file_name = "jobs.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    print("Creating database and tables...")
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     create_db_and_tables()
#     yield


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


class JobCreate(BaseModel):
    job_id: str


@app.post("/job/", response_model_exclude_none=True)
async def create_job(job: JobCreate, session: SessionDep) -> Job:
    job_id = job.job_id
    if session.get(Job, job_id):
        raise HTTPException(status_code=400, detail="Job ID already exists")
    print("Creating job with ID:", job_id)
    job = Job(job_id=job_id, status="QUEUED", submitted_at=datetime.datetime.now())
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@app.patch("/job/{job_id}", response_model_exclude_none=True)
def update_job(job_id: str, job: Job, session: SessionDep) -> Job:
    stored_job = session.get(Job, job_id)
    if not stored_job:
        raise HTTPException(status_code=404, detail="Job not found")
    # TODO: enforce only change queued --> running|failed
    # TODO: enforce only change running --> failed|finished
    job_data = job.model_dump(exclude_unset=True)
    stored_job.sqlmodel_update(job_data)
    session.add(stored_job)
    session.commit()
    session.refresh(stored_job)
    return stored_job


@app.get("/job/{job_id}", response_model_exclude_none=True)
def retrieve_job(job_id: str, session: SessionDep) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
