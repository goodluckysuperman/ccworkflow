from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app


def test_install_execute_requires_conflict_resolutions_for_conflicts(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    project_root = tmp_path / "project"
    project_root.mkdir()
    existing_skill = project_root / ".claude" / "skills" / "conflict-skill" / "SKILL.md"
    existing_skill.parent.mkdir(parents=True)
    existing_skill.write_text("# Existing", encoding="utf-8")

    client = TestClient(create_app())
    create_response = client.post(
        "/api/packages",
        json={
            "name": "conflict package",
            "summary": "conflict summary",
            "tags": ["conflict"],
            "objects": [
                {
                    "type": "skill",
                    "name": "conflict-skill",
                    "description": "skill",
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

    execute_response = client.post(
        "/api/install/execute",
        json={
            "package_id": package_id,
            "scope": "project",
            "project_root": str(project_root),
            "resolutions": [],
        },
    )

    assert execute_response.status_code == 200
    assert execute_response.json()["success"] is False
    assert "冲突" in execute_response.json()["message"]
