from pathlib import Path

from fastapi.testclient import TestClient

from ccworkflow.app.factory import create_app
from ccworkflow.app.runtime import get_collection_root


def test_settings_api_and_page(tmp_path) -> None:
    client = TestClient(create_app())

    page_response = client.get("/settings")
    assert page_response.status_code == 200
    assert "设置" in page_response.text

    get_response = client.get("/api/settings")
    assert get_response.status_code == 200
    assert get_response.json()["success"] is True

    update_response = client.put(
        "/api/settings",
        json={"last_generate_mode": "ai", "last_install_scope": "global"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["settings"]["last_generate_mode"] == "ai"
    assert update_response.json()["data"]["settings"]["last_install_scope"] == "global"


def test_migrate_root_moves_collection_data(tmp_path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("print('ok')", encoding="utf-8")
    client = TestClient(create_app())

    create_response = client.post(
        "/api/packages",
        json={
            "name": "migrate package",
            "summary": "migrate summary",
            "tags": ["settings"],
            "objects": [
                {
                    "type": "skill",
                    "name": "migrate-skill",
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
    assert create_response.json()["success"] is True

    current_root = get_collection_root()
    new_root = tmp_path / "migrated-root"
    response = client.post("/api/settings/migrate-root", json={"new_root": str(new_root)})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert (new_root / "skills").exists()
    assert any((new_root / "skills").iterdir())
