import json
from pathlib import Path

from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.install_record_repository import load_record, mark_uninstall_result
from ccworkflow.infra.fs_gateway import delete_path
from ccworkflow.infra.json_gateway import read_json, write_json


def uninstall_by_record(input_data: dict) -> dict:
    record_id = input_data["install_record_id"]
    record_path = get_collection_root() / "install_records" / f"{record_id}.json"
    if not record_path.exists():
        return AppResult(success=False, message="安装记录不存在").model_dump()

    record = load_record({"record_path": str(record_path)})["data"]["record"]
    removed_objects: list[str] = []
    removed_scripts: list[str] = []
    blocked_objects: list[str] = []

    for entry in record.get("entries", []):
        target_file = Path(entry["target_file"])
        if not target_file.exists():
            removed_objects.append(entry["object_id"])
            continue

        if entry["type"] == "skill":
            current_content = target_file.read_text(encoding="utf-8")
            if current_content != entry.get("snapshot"):
                blocked_objects.append(entry["object_id"])
                continue
            delete_path(target_file)
            removed_objects.append(entry["object_id"])
            continue

        payload = read_json(target_file)
        if entry["type"] == "hook":
            generated = payload.get("generatedHooks", {})
            snapshot = entry.get("snapshot", {})
            key = next(iter(snapshot.keys()), None)
            if key is None or generated.get(key) != snapshot.get(key):
                blocked_objects.append(entry["object_id"])
                continue
            generated.pop(key, None)
            payload["generatedHooks"] = generated
            write_json(target_file, payload)
            removed_objects.append(entry["object_id"])
            continue

        if entry["type"] == "mcp":
            mcp_servers = payload.get("mcpServers", {})
            snapshot = entry.get("snapshot", {})
            key = next(iter(snapshot.keys()), None)
            if key is None or mcp_servers.get(key) != snapshot.get(key):
                blocked_objects.append(entry["object_id"])
                continue
            mcp_servers.pop(key, None)
            payload["mcpServers"] = mcp_servers
            write_json(target_file, payload)
            removed_objects.append(entry["object_id"])

    for script_path in record.get("copied_scripts", []):
        target = Path(script_path)
        if target.exists():
            delete_path(target)
            removed_scripts.append(target.as_posix())

    uninstall_status = "uninstall_failed" if blocked_objects else "uninstall_success"
    updated = mark_uninstall_result({"record_path": str(record_path), "uninstall_status": uninstall_status})
    return AppResult(
        success=not blocked_objects,
        data={
            "install_record_id": record_id,
            "removed_objects": removed_objects,
            "removed_scripts": removed_scripts,
            "blocked_objects": blocked_objects,
            "record": updated["data"]["record"],
        },
    ).model_dump()
