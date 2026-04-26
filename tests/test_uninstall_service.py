from pathlib import Path

from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app
from ccworkflow.app.runtime import get_collection_root


def test_uninstall_removes_installed_files(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    project_root = tmp_path / "project"
    project_root.mkdir()
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "uninstall package",
            "summary": "uninstall summary",
            "tags": ["uninstall"],
            "objects": [
                {
                    "type": "skill",
                    "name": "uninstall-skill",
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
        json={"package_id": package_id, "scope": "project", "project_root": str(project_root), "resolutions": []},
    )
    record_id = execute_response.json()["data"]["install_record_id"]

    uninstall_response = client.post(f"/api/install/uninstall/{record_id}")
    assert uninstall_response.status_code == 200
    assert uninstall_response.json()["success"] is True
    assert not (project_root / ".claude" / "skills" / "uninstall-skill" / "SKILL.md").exists()
    assert not (project_root / ".claude" / "scripts" / "helper.py").exists()


def test_uninstall_blocks_modified_skill_file(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    project_root = tmp_path / "project"
    project_root.mkdir()
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "blocked uninstall package",
            "summary": "blocked uninstall",
            "tags": ["uninstall"],
            "objects": [
                {
                    "type": "skill",
                    "name": "blocked-skill",
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
        json={"package_id": package_id, "scope": "project", "project_root": str(project_root), "resolutions": []},
    )
    record_id = execute_response.json()["data"]["install_record_id"]

    skill_file = project_root / ".claude" / "skills" / "blocked-skill" / "SKILL.md"
    skill_file.write_text("# Modified", encoding="utf-8")

    uninstall_response = client.post(f"/api/install/uninstall/{record_id}")
    assert uninstall_response.status_code == 200
    assert uninstall_response.json()["success"] is False
    assert uninstall_response.json()["data"]["blocked_objects"]
    assert skill_file.exists()
    assert (project_root / ".claude" / "scripts" / "helper.py").exists()
