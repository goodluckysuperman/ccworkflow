from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app
from ccworkflow.domain.common_schema import AppResult


def test_generate_page_renders_when_claude_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        "ccworkflow.web.routes.page_routes.check_available",
        lambda _: AppResult(success=True, data={"available": False, "version": ""}).model_dump(),
    )
    client = TestClient(create_app())

    response = client.get("/generate")

    assert response.status_code == 200
    assert "AI 生成草稿" in response.text
    assert "Claude Code 当前不可用" in response.text


def test_generate_api_returns_draft(monkeypatch) -> None:
    monkeypatch.setattr(
        "ccworkflow.web.routes.generate_routes.generate_draft",
        lambda payload: AppResult(
            success=True,
            data={
                "draft": {
                    "package_id": None,
                    "name": payload["name"],
                    "summary": payload["summary"],
                    "tags": payload["tags"],
                    "objects": [
                        {
                            "object_id": None,
                            "type": "skill",
                            "name": "generated-skill",
                            "description": "generated",
                            "body": "# Skill",
                            "extra": {},
                        }
                    ],
                    "scripts": [],
                },
                "warnings": [],
                "claude_version": "claude-test",
            },
        ).model_dump(),
    )
    client = TestClient(create_app())

    response = client.post(
        "/api/generate/draft",
        json={
            "name": "ai package",
            "summary": "summary",
            "tags": ["ai"],
            "target_types": ["skill"],
            "prompt": "生成一个 skill",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["draft"]["name"] == "ai package"
