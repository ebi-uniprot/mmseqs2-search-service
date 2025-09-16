import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Import the FastAPI app and dependency from the module where the code is defined
from main import app, get_session

from pathlib import Path
import json

mock_dir = Path("../mocks")
with open(mock_dir / "worker_send_job_running_to_db.json") as f:
    worker_send_job_running_to_db = json.load(f)

with open(mock_dir / "db_get_queued_job.json") as f:
    db_get_queued_job = json.load(f)


@pytest.fixture
def client():
    # Set up an in-memory SQLite database for testing (no file name means in-memory)
    test_engine = create_engine(
        "sqlite://",  # In-memory database URL [oai_citation:5‡sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#:~:text=2,file%20name%2C%20leave%20it%20empty)
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Use StaticPool to persist data across connections [oai_citation:6‡sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#:~:text=1.%20Import%20,use%20it%20in%20a%20bit)
    )
    # Create all database tables on the test engine
    SQLModel.metadata.create_all(test_engine)  # Ensure tables exist for tests

    # Dependency override to use test session
    def override_get_session():
        # Use contextmanager to ensure session is closed after each request
        with Session(test_engine) as session:
            yield session

    # Override the get_session dependency in FastAPI app [oai_citation:7‡sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#:~:text=from%20,%281)
    app.dependency_overrides[get_session] = override_get_session

    # Create a TestClient using the FastAPI app
    with TestClient(app) as test_client:
        yield test_client
    # Clear overrides after tests to avoid side effects
    app.dependency_overrides.clear()


def test_full_job_lifecycle_success(client):
    response = client.post(
        "/job/", json={"job_id": worker_send_job_running_to_db["job_id"]}
    )
    assert response.status_code == 200
    assert response.json() == {}  # Endpoint returns an empty dict on success


def test_get_job_when_job_does_not_exist(client):
    response = client.get(f"/job/{db_get_queued_job['job_id']}")
    assert response.status_code == 404
