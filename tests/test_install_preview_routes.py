import json

from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app


def test_preview_install_returns_targets(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    project_root = tmp_path / "project"
    project_root.mkdir()
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "install package",
            "summary": "preview package",
            "tags": ["install"],
            "objects": [
                {
                    "type": "skill",
                    "name": "preview-skill",
                    "description": "preview skill",
                    "body": "# Skill\n{{script:helper.py}}",
                    "extra": {},
                }
            ],
            "scripts": [
                {
                    "name": "helper.py",
                    "source_path": str(helper),
                    "applies_to": [],
                }
            ],
        },
    )
    package_id = create_response.json()["data"]["package_id"]

    preview_response = client.post(
        "/api/install/preview",
        json={
            "package_id": package_id,
            "scope": "project",
            "project_root": str(project_root),
        },
    )

    assert preview_response.status_code == 200
    payload = preview_response.json()
    assert payload["success"] is True
    assert any(item.endswith(".claude/skills/preview-skill/SKILL.md") for item in payload["data"]["target_files"])
    assert payload["data"]["conflicts"] == []
