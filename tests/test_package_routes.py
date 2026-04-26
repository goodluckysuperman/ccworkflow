from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app


def test_create_and_list_packages_via_api(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "api package",
            "summary": "via api",
            "tags": ["api"],
            "objects": [
                {
                    "type": "skill",
                    "name": "api-skill",
                    "description": "api skill",
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

    assert create_response.status_code == 200
    assert create_response.json()["success"] is True
    package_id = create_response.json()["data"]["package_id"]

    list_response = client.get("/api/packages", params={"keyword": "api"})
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] >= 1

    update_response = client.put(
        f"/api/packages/{package_id}",
        json={
            "name": "api package updated",
            "summary": "updated",
            "tags": ["api", "updated"],
            "objects": [
                {
                    "type": "skill",
                    "name": "api-skill-updated",
                    "description": "api skill updated",
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

    assert update_response.status_code == 200
    assert update_response.json()["success"] is True

    detail_response = client.get(f"/api/packages/{package_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["package"]["name"] == "api package updated"
