from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app


def test_install_record_pages_and_api(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    project_root = tmp_path / "project"
    project_root.mkdir()
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "record package",
            "summary": "record summary",
            "tags": ["record"],
            "objects": [
                {
                    "type": "skill",
                    "name": "record-skill",
                    "description": "record skill",
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

    list_response = client.get("/api/install-records")
    assert list_response.status_code == 200
    assert any(item["install_record_id"] == record_id for item in list_response.json()["data"]["items"])

    detail_response = client.get(f"/api/install-records/{record_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["record"]["install_record_id"] == record_id

    page_response = client.get("/install-records")
    assert page_response.status_code == 200
    assert "安装记录" in page_response.text
    assert "卸载" in page_response.text
    assert "查看详情" in page_response.text
