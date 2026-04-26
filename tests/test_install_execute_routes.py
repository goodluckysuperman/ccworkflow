import json

from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app
from ccworkflow.app.runtime import get_collection_root
from ccworkflow.repositories.install_record_repository import list_records


def test_execute_install_creates_record_and_writes_files(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    project_root = tmp_path / "project"
    project_root.mkdir()
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "execute package",
            "summary": "execute install",
            "tags": ["install"],
            "objects": [
                {
                    "type": "skill",
                    "name": "exec-skill",
                    "description": "exec skill",
                    "body": "# Skill\n{{script:helper.py}}",
                    "extra": {},
                },
                {
                    "type": "mcp",
                    "name": "exec-mcp",
                    "description": "exec mcp",
                    "body": {"command": "python", "args": [], "env": {}},
                    "extra": {"server_name": "exec-mcp"},
                },
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
    payload = execute_response.json()
    assert payload["success"] is True
    assert (project_root / ".claude" / "skills" / "exec-skill" / "SKILL.md").exists()
    assert (project_root / ".mcp.json").exists()
    assert (project_root / ".claude" / "scripts" / "helper.py").exists()

    records_dir = get_collection_root() / "install_records"
    records_result = list_records({"records_dir": str(records_dir)})
    assert records_result["success"] is True
    assert len(records_result["data"]["items"]) >= 1
    assert any(item["install_record_id"] == payload["data"]["install_record_id"] for item in records_result["data"]["items"])
