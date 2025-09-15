import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("endpoint", "method", "status_code", "response_json"),
    [
        ("/", "get", 200, {"status": "ok"}),
        ("/submit/", "post", 200, {"status": "ok"}),
        ("/status/12345", "get", 200, {"status": "ok"}),
        ("/results/12345", "get", 200, {"status": "ok", "uuid": "12345"}),
    ],
)
def test_read_main(client: TestClient, endpoint: str, method: str, status_code: int, response_json: dict) -> None:
    """Test all possible endpoints."""
    response = client.request(method, endpoint)
    assert response.status_code == status_code
    assert response.json() == response_json
