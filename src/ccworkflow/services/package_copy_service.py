from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.package_repository import find_package_dir, load_bundle
from ccworkflow.services.package_save_service import save_package


def copy_package(input_data: dict) -> dict:
    package_id = input_data["package_id"]
    new_name = input_data["new_name"]
    collection_root = get_collection_root()

    found = find_package_dir({"package_id": package_id, "collection_root": str(collection_root)})
    if not found["success"]:
        return AppResult(success=False, message="源配置包不存在").model_dump()

    bundle = load_bundle({"package_dir": found["data"]["package_dir"]})["data"]["bundle"]
    package = bundle["package"]
    package["package_id"] = None
    package["name"] = new_name
    for obj in package["objects"]:
        obj["object_id"] = None
    for script in package["scripts"]:
        script["script_id"] = None

    result = save_package({"package": package, "save_mode": "create"})
    if not result["success"]:
        return result

    return AppResult(
        success=True,
        data={
            "source_package_id": package_id,
            "new_package_id": result["data"]["package_id"],
        },
    ).model_dump()
