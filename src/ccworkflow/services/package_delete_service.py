from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.package_repository import delete_bundle, find_package_dir


def delete_package(input_data: dict) -> dict:
    package_id = input_data["package_id"]
    collection_root = get_collection_root()
    found = find_package_dir({"package_id": package_id, "collection_root": str(collection_root)})
    if not found["success"]:
        return AppResult(success=False, message="配置包不存在").model_dump()

    delete_bundle({"package_dir": found["data"]["package_dir"]})
    return AppResult(success=True, data={"package_id": package_id, "deleted": True}).model_dump()
