import uuid
from pathlib import Path

from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.enums import ObjectType
from ccworkflow.domain.record_schema import InstallRecordDraft
from ccworkflow.infra.fs_gateway import copy_file
from ccworkflow.infra.time_gateway import now_iso
from ccworkflow.installers.hook_installer import install_hook
from ccworkflow.installers.mcp_installer import install_mcp
from ccworkflow.installers.skill_installer import install_skill
from ccworkflow.repositories.install_record_repository import save_record
from ccworkflow.services.install_preview_service import preview_install


def execute_install(input_data: dict) -> dict:
    preview = preview_install(
        {
            "package_id": input_data["package_id"],
            "scope": input_data["scope"],
            "project_root": input_data.get("project_root"),
        }
    )
    if not preview["success"]:
        return preview

    copied_scripts = _copy_scripts(preview["data"]["copied_scripts"])
    resolutions = {item["object_id"]: item["action"] for item in input_data.get("resolutions", [])}
    objects = preview["data"]["resolved_objects"]
    targets = {item["object_id"]: item for item in preview["data"]["targets"]}

    installed_objects: list[str] = []
    skipped_objects: list[str] = []
    failed_objects: list[str] = []
    written_files: list[str] = []
    entries: list[dict] = []

    for obj in objects:
        resolution = resolutions.get(obj["object_id"], "replace")
        target = targets[obj["object_id"]]
        result = _install_single_object(obj, target, resolution)
        if not result["success"]:
            failed_objects.append(obj["object_id"])
            if resolution == "cancel":
                return AppResult(success=False, message="安装已取消", data={"failed_objects": failed_objects}).model_dump()
            continue

        data = result["data"]
        if data.get("skipped"):
            skipped_objects.append(obj["object_id"])
            continue

        installed_objects.append(obj["object_id"])
        if data.get("written_file"):
            written_files.append(data["written_file"])
        entries.append(
            {
                "object_id": obj["object_id"],
                "type": obj["type"],
                "target_file": target["target_file"],
                "snapshot": data.get("snapshot"),
            }
        )

    install_record_id = f"inst_{uuid.uuid4().hex[:12]}"
    collection_root = get_collection_root()
    record_path = Path(collection_root) / "install_records" / f"{install_record_id}.json"
    record = InstallRecordDraft(
        install_record_id=install_record_id,
        package_id=input_data["package_id"],
        scope=input_data["scope"],
        project_root=input_data.get("project_root"),
        installed_at=now_iso(),
        install_status="success" if not failed_objects else "partial_failed",
        installed_objects=installed_objects,
        skipped_objects=skipped_objects,
        failed_objects=failed_objects,
        written_files=written_files,
        copied_scripts=[item["target_path"] for item in copied_scripts],
        conflict_resolutions=input_data.get("resolutions", []),
        entries=entries,
    )
    save_record({"record": record.model_dump(mode="json"), "record_path": str(record_path)})

    return AppResult(
        success=True,
        data={
            "install_record_id": install_record_id,
            "installed_objects": installed_objects,
            "skipped_objects": skipped_objects,
            "failed_objects": failed_objects,
            "written_files": written_files,
            "copied_scripts": [item["target_path"] for item in copied_scripts],
        },
    ).model_dump()


def _install_single_object(obj: dict, target: dict, resolution: str) -> dict:
    object_type = ObjectType(obj["type"])
    payload = {"object": obj, "target_file": target["target_file"], "resolution": resolution}
    if object_type == ObjectType.SKILL:
        return install_skill(payload)
    if object_type == ObjectType.HOOK:
        return install_hook(payload)
    return install_mcp(payload)


def _copy_scripts(items: list[dict]) -> list[dict]:
    copied: list[dict] = []
    for item in items:
        copy_file(item["source_path"], item["target_path"])
        copied.append(item)
    return copied
