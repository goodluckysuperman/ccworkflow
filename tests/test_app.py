from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app


def test_home_page_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "ccworkflow" in response.text
