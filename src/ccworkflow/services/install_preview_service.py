from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.installers.conflict_detector import detect_conflicts
from ccworkflow.installers.script_materializer import materialize_scripts
from ccworkflow.installers.target_path_resolver import resolve_targets
from ccworkflow.repositories.package_repository import find_package_dir, load_bundle


def preview_install(input_data: dict) -> dict:
    package_id = input_data["package_id"]
    scope = input_data["scope"]
    project_root = input_data.get("project_root")
    collection_root = get_collection_root()

    found = find_package_dir({"package_id": package_id, "collection_root": str(collection_root)})
    if not found["success"]:
        return AppResult(success=False, message="配置包不存在").model_dump()

    bundle = load_bundle({"package_dir": found["data"]["package_dir"]})["data"]["bundle"]
    package = bundle["package"]

    materialized = materialize_scripts(
        {
            "scope": scope,
            "project_root": project_root,
            "objects": package["objects"],
            "scripts": package["scripts"],
        }
    )
    if not materialized["success"]:
        return materialized

    resolved_objects = materialized["data"]["resolved_objects"]
    targets_result = resolve_targets(
        {
            "scope": scope,
            "project_root": project_root,
            "objects": resolved_objects,
        }
    )
    if not targets_result["success"]:
        return targets_result

    conflicts_result = detect_conflicts(
        {
            "targets": targets_result["data"]["targets"],
            "objects": resolved_objects,
        }
    )

    target_files = sorted({target["target_file"] for target in targets_result["data"]["targets"]})
    return AppResult(
        success=True,
        data={
            "package_id": package_id,
            "scope": scope,
            "target_files": target_files,
            "missing_scripts": materialized["data"].get("missing_scripts", []),
            "copied_scripts": materialized["data"]["copied_scripts"],
            "conflicts": conflicts_result["data"]["conflicts"],
            "cancel_allowed": True,
            "resolved_objects": resolved_objects,
            "targets": targets_result["data"]["targets"],
        },
    ).model_dump()
