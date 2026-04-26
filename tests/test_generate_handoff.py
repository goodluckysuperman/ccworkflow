from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app
from ccworkflow.domain.common_schema import AppResult


def test_generate_page_supports_edit_draft_handoff(monkeypatch) -> None:
    monkeypatch.setattr(
        "ccworkflow.web.routes.page_routes.check_available",
        lambda _: AppResult(success=True, data={"available": True, "version": "claude-test"}).model_dump(),
    )
    client = TestClient(create_app())

    response = client.get("/generate")

    assert response.status_code == 200
    assert "继续编辑" in response.text


def test_new_package_page_can_accept_draft_flag() -> None:
    client = TestClient(create_app())

    response = client.get("/packages/new", params={"from_draft": 1})

    assert response.status_code == 200
    assert "新增对象" in response.text
