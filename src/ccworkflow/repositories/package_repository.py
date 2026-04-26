from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.package_manifest_schema import PackageBundle, PackageManifest
from ccworkflow.domain.package_schema import PackageDraft
from ccworkflow.infra.fs_gateway import copy_file, delete_path, ensure_dir
from ccworkflow.infra.json_gateway import read_json, write_json


def save_bundle(input_data: dict) -> dict:
    package = PackageDraft.model_validate(input_data["package"])
    manifest = PackageManifest.model_validate(input_data["manifest"])
    package_dir = ensure_dir(input_data["package_dir"])
    objects_dir = ensure_dir(package_dir / "objects")
    scripts_dir = ensure_dir(package_dir / "scripts")

    write_json(package_dir / "manifest.json", manifest.model_dump())

    for index, obj in enumerate(package.objects, start=1):
        write_json(objects_dir / f"{index:02d}_{obj.object_id}.json", obj.model_dump(mode="json"))

    for script in package.scripts:
        copy_file(script.source_path, scripts_dir / f"{script.script_id}__{script.name}")

    return AppResult(
        success=True,
        data={
            "package_id": manifest.package_id,
            "package_dir": str(package_dir),
        },
    ).model_dump()


def load_bundle(input_data: dict) -> dict:
    package_dir = input_data["package_dir"]
    manifest_payload = read_json(f"{package_dir}/manifest.json")
    manifest = PackageManifest.model_validate(manifest_payload)

    object_payloads: list[dict] = []
    for object_id in manifest.object_ids:
        matches = list((ensure_dir(f"{package_dir}/objects")).glob(f"*_{object_id}.json"))
        if matches:
            object_payloads.append(read_json(matches[0]))

    scripts: list[dict] = []
    scripts_dir = ensure_dir(f"{package_dir}/scripts")
    for script_id in manifest.script_ids:
        matches = list(scripts_dir.glob(f"{script_id}__*"))
        if matches:
            scripts.append(
                {
                    "script_id": script_id,
                    "name": matches[0].name.split("__", 1)[1],
                    "source_path": str(matches[0]),
                    "applies_to": [],
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
    collection_root = input_data["collection_root"]
    items: list[dict] = []
    for category in ["skills", "hooks", "mcp", "mixed"]:
        category_dir = ensure_dir(f"{collection_root}/{category}")
        for package_dir in category_dir.iterdir():
            manifest_path = package_dir / "manifest.json"
            if package_dir.is_dir() and manifest_path.exists():
                items.append(read_json(manifest_path))
    items.sort(key=lambda item: item["updated_at"], reverse=True)
    return AppResult(success=True, data={"items": items}).model_dump()


def delete_bundle(input_data: dict) -> dict:
    delete_path(input_data["package_dir"])
    return AppResult(success=True, data={"deleted": True}).model_dump()
