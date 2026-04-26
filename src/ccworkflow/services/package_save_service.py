import uuid
from pathlib import Path

from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.package_manifest_schema import PackageManifest, ScriptMeta
from ccworkflow.domain.package_schema import PackageDraft
from ccworkflow.infra.time_gateway import now_iso
from ccworkflow.repositories.package_repository import delete_bundle, find_package_dir, load_bundle, save_bundle
from ccworkflow.services.package_validation_service import validate_package


def save_package(input_data: dict) -> dict:
    package = PackageDraft.model_validate(input_data["package"])
    save_mode = input_data["save_mode"]
    collection_root = get_collection_root()

    existing_bundle = None
    existing_dir = None
    if package.package_id:
        existing_lookup = find_package_dir({"package_id": package.package_id, "collection_root": str(collection_root)})
        if existing_lookup["success"]:
            existing_dir = existing_lookup["data"]["package_dir"]
            existing_bundle = load_bundle({"package_dir": existing_dir})["data"]["bundle"]
        elif save_mode == "update":
            return AppResult(success=False, message="配置包不存在").model_dump()

    validation = validate_package({"package": package.model_dump(mode="json")})
    if not validation["success"]:
        return validation

    timestamp = now_iso()
    package_id = package.package_id or f"pkg_{uuid.uuid4().hex[:12]}"
    object_ids: list[str] = []
    normalized_objects: list[dict] = []
    for obj in package.objects:
        object_id = obj.object_id or f"obj_{uuid.uuid4().hex[:12]}"
        object_ids.append(object_id)
        normalized = obj.model_dump(mode="json")
        normalized["object_id"] = object_id
        normalized_objects.append(normalized)

    script_ids: list[str] = []
    normalized_scripts: list[dict] = []
    script_meta_items: list[ScriptMeta] = []
    for script in package.scripts:
        script_id = script.script_id or f"script_{uuid.uuid4().hex[:12]}"
        script_ids.append(script_id)
        normalized = script.model_dump(mode="json")
        normalized["script_id"] = script_id
        normalized_scripts.append(normalized)
        script_meta_items.append(
            ScriptMeta(
                script_id=script_id,
                name=script.name,
                stored_filename=f"{script_id}__{script.name}",
                applies_to=script.applies_to,
            )
        )

    normalized_package = PackageDraft.model_validate(
        {
            "package_id": package_id,
            "name": package.name,
            "summary": package.summary,
            "tags": package.tags,
            "objects": normalized_objects,
            "scripts": normalized_scripts,
        }
    )

    category = validation["data"]["category"]
    package_dir = Path(collection_root) / category / package_id
    created_at = input_data.get("created_at") or (existing_bundle and existing_bundle["manifest"]["created_at"]) or timestamp
    manifest = PackageManifest(
        package_id=package_id,
        name=normalized_package.name,
        summary=normalized_package.summary,
        tags=normalized_package.tags,
        category=category,
        object_types=sorted({obj.type.value for obj in normalized_package.objects}),
        object_ids=object_ids,
        script_ids=script_ids,
        scripts_meta=script_meta_items,
        created_at=created_at,
        updated_at=timestamp,
        status="saved",
    )

    save_bundle(
        {
            "package": normalized_package.model_dump(mode="json"),
            "manifest": manifest.model_dump(mode="json"),
            "package_dir": str(package_dir),
        }
    )

    if existing_dir and Path(existing_dir) != package_dir:
        delete_bundle({"package_dir": existing_dir})

    return AppResult(
        success=True,
        data={
            "package_id": package_id,
            "category": category,
            "package_dir": str(package_dir),
            "updated_at": timestamp,
            "created_at": created_at,
            "save_mode": save_mode,
        },
    ).model_dump()
