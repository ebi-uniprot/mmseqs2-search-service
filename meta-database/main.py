import datetime
from typing import Union, Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from sqlmodel import Field, Session, SQLModel, create_engine

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
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


@app.post("/")
def create_job(job_id: str, session: SessionDep):
    job = Job(job_id=job_id, status="created", submitted_at=datetime.datetime.now())
    session.add(job)
    session.commit()
    session.refresh(job)
    return {}

@app.patch("/{job_id}")
def update_job(job_id: str, job: Job, session: SessionDep) -> Job:
    job_db = session.get(Job, job_id)
    if not job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.model_dump(exclude_unset=True) 
    job_db.sqlmodel_update(job_data)
    session.add(job_db)
    session.commit()
    session.refresh(job_db)
    return job_db

@app.get("/{job_id}")
def retrieve_job(job_id: str, session: SessionDep) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job