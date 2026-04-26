from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app


def test_home_page_shows_package_list_page() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "配置包列表" in response.text


def test_package_pages_render_detail_and_edit(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "page package",
            "summary": "page summary",
            "tags": ["ui"],
            "objects": [
                {
                    "type": "skill",
                    "name": "page-skill",
                    "description": "page skill",
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

    detail_response = client.get(f"/packages/{package_id}")
    assert detail_response.status_code == 200
    assert "page package" in detail_response.text
    assert "page-skill" in detail_response.text

    edit_response = client.get(f"/packages/{package_id}/edit")
    assert edit_response.status_code == 200
    assert "编辑配置包" in edit_response.text
    assert "page package" in edit_response.text
