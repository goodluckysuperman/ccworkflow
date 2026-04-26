from pathlib import Path

from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.package_repository import delete_bundle


def delete_package(input_data: dict) -> dict:
    package_id = input_data["package_id"]
    collection_root = get_collection_root()

    for category in ["skills", "hooks", "mcp", "mixed"]:
        package_dir = Path(collection_root) / category / package_id
        if package_dir.exists():
            delete_bundle({"package_dir": str(package_dir)})
            return AppResult(success=True, data={"package_id": package_id, "deleted": True}).model_dump()

    return AppResult(success=False, message="配置包不存在").model_dump()
