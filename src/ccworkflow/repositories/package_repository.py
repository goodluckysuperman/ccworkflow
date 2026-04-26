from pathlib import Path

from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.package_manifest_schema import PackageBundle, PackageManifest
from ccworkflow.domain.package_schema import PackageDraft
from ccworkflow.infra.fs_gateway import copy_file, delete_path, ensure_dir
from ccworkflow.infra.json_gateway import read_json, write_json


CATEGORIES = ["skills", "hooks", "mcp", "mixed"]


def save_bundle(input_data: dict) -> dict:
    package = PackageDraft.model_validate(input_data["package"])
    manifest = PackageManifest.model_validate(input_data["manifest"])
    package_dir = ensure_dir(input_data["package_dir"])

    delete_path(package_dir / "objects")
    delete_path(package_dir / "scripts")
    objects_dir = ensure_dir(package_dir / "objects")
    scripts_dir = ensure_dir(package_dir / "scripts")

    write_json(package_dir / "manifest.json", manifest.model_dump(mode="json"))

    for index, obj in enumerate(package.objects, start=1):
        write_json(objects_dir / f"{index:02d}_{obj.object_id}.json", obj.model_dump(mode="json"))

    for script_meta, script in zip(manifest.scripts_meta, package.scripts, strict=False):
        copy_file(script.source_path, scripts_dir / script_meta.stored_filename)

    return AppResult(
        success=True,
        data={
            "package_id": manifest.package_id,
            "package_dir": str(package_dir),
        },
    ).model_dump()


def load_bundle(input_data: dict) -> dict:
    package_dir = Path(input_data["package_dir"])
    manifest_payload = read_json(package_dir / "manifest.json")
    manifest = PackageManifest.model_validate(manifest_payload)

    object_payloads: list[dict] = []
    objects_dir = package_dir / "objects"
    for object_id in manifest.object_ids:
        matches = list(objects_dir.glob(f"*_{object_id}.json"))
        if matches:
            object_payloads.append(read_json(matches[0]))

    scripts: list[dict] = []
    scripts_dir = package_dir / "scripts"
    for script_meta in manifest.scripts_meta:
        script_path = scripts_dir / script_meta.stored_filename
        scripts.append(
            {
                "script_id": script_meta.script_id,
                "name": script_meta.name,
                "source_path": str(script_path),
                "applies_to": script_meta.applies_to,
            }
        )

    package = PackageDraft.model_validate(
        {
            "package_id": manifest.package_id,
            "name": manifest.name,
            "summary": manifest.summary,
            "tags": manifest.tags,
            "objects": object_payloads,
            "scripts": scripts,
        }
    )

    bundle = PackageBundle(package=package, manifest=manifest, package_dir=str(package_dir))
    return AppResult(success=True, data={"bundle": bundle.model_dump(mode="json")}).model_dump()


def list_manifests(input_data: dict) -> dict:
    collection_root = Path(input_data["collection_root"])
    items: list[dict] = []
    for category in CATEGORIES:
        category_dir = ensure_dir(collection_root / category)
        for package_dir in category_dir.iterdir():
            manifest_path = package_dir / "manifest.json"
            if package_dir.is_dir() and manifest_path.exists():
                items.append(read_json(manifest_path))
    items.sort(key=lambda item: item["updated_at"], reverse=True)
    return AppResult(success=True, data={"items": items}).model_dump()


def delete_bundle(input_data: dict) -> dict:
    delete_path(input_data["package_dir"])
    return AppResult(success=True, data={"deleted": True}).model_dump()


def find_package_dir(input_data: dict) -> dict:
    package_id = input_data["package_id"]
    collection_root = Path(input_data["collection_root"])
    for category in CATEGORIES:
        package_dir = collection_root / category / package_id
        if package_dir.exists():
            return AppResult(success=True, data={"package_dir": str(package_dir)}).model_dump()
    return AppResult(success=False, message="配置包不存在").model_dump()
