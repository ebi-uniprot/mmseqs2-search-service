"""Metadata db models and handlers."""

from datetime import datetime

from pydantic import BaseModel

from api.status import TaskStatus


class MetadataDbGetRequest(BaseModel):
    """Object that we send to the metadata db with handlers via GET."""

    job_id: str


class MetadataDbPostRequest(BaseModel):
    """Object that we send to the metadata db with handlers via POST."""

    job_id: str


class MetaDataDbPostResponse(BaseModel):
    """Object that we receive from the metadata db with handlers via POST."""

    job_id: str
    status: TaskStatus


class MetaDataDbGetResponse(BaseModel):
    """Object that we receive from the metadata db with handlers via GET."""

    job_id: str
    status: TaskStatus
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
