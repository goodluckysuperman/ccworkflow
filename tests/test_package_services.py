from pathlib import Path

from ccworkflow.services.package_copy_service import copy_package
from ccworkflow.services.package_delete_service import delete_package
from ccworkflow.services.package_query_service import get_package_detail, list_packages
from ccworkflow.services.package_save_service import save_package
from ccworkflow.services.package_validation_service import validate_package


def _sample_package(script_path: Path) -> dict:
    return {
        "name": "demo skill package",
        "summary": "first package",
        "tags": ["python", "review"],
        "objects": [
            {
                "type": "skill",
                "name": "python-review",
                "description": "review skill",
                "body": "# Skill\nUse {{script:helper.py}} to assist.",
                "extra": {},
            }
        ],
        "scripts": [
            {
                "name": "helper.py",
                "source_path": str(script_path),
                "applies_to": [],
            }
        ],
    }


def test_validate_package_rejects_missing_name(tmp_path: Path) -> None:
    script = tmp_path / "helper.py"
    script.write_text("print('ok')", encoding="utf-8")
    payload = _sample_package(script)
    payload["name"] = ""

    result = validate_package({"package": payload})

    assert result["success"] is False
    assert any(error["code"] == "PACKAGE_NAME_REQUIRED" for error in result["errors"])


def test_save_query_copy_delete_package_flow(tmp_path: Path) -> None:
    script = tmp_path / "helper.py"
    script.write_text("print('ok')", encoding="utf-8")

    save_result = save_package({"package": _sample_package(script), "save_mode": "create"})
    assert save_result["success"] is True
    package_id = save_result["data"]["package_id"]

    detail_result = get_package_detail({"package_id": package_id})
    assert detail_result["success"] is True
    assert detail_result["data"]["package"]["name"] == "demo skill package"

    list_result = list_packages({"keyword": "demo", "tags": ["python"], "type": "skill"})
    assert list_result["success"] is True
    assert list_result["data"]["total"] == 1

    copy_result = copy_package({"package_id": package_id, "new_name": "demo skill package copy"})
    assert copy_result["success"] is True
    copied_id = copy_result["data"]["new_package_id"]
    assert copied_id != package_id

    delete_result = delete_package({"package_id": package_id})
    assert delete_result["success"] is True

    deleted_detail = get_package_detail({"package_id": package_id})
    assert deleted_detail["success"] is False
