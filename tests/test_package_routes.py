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

    list_response = client.get("/api/packages", params={"keyword": "api"})
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] >= 1
