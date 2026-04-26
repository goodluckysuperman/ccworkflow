import json
from pathlib import Path

from ccworkflow.infra.fs_gateway import ensure_dir
from ccworkflow.infra.json_gateway import read_json, write_json


def install_hook(input_data: dict) -> dict:
    obj = input_data["object"]
    target_file = Path(input_data["target_file"])
    resolution = input_data["resolution"]
    if resolution == "skip":
        return {"success": True, "data": {"object_id": obj["object_id"], "skipped": True, "written_file": None, "snapshot": None}}
    if resolution == "cancel":
        return {"success": False, "message": "安装已取消", "data": {"object_id": obj["object_id"]}}

    ensure_dir(target_file.parent)
    payload = read_json(target_file) if target_file.exists() else {}
    hook_entries = payload.get("generatedHooks", {}) if isinstance(payload, dict) else {}
    hook_key = obj.get("extra", {}).get("hook_key") or obj["name"]
    hook_entries[hook_key] = obj["body"]
    payload["generatedHooks"] = hook_entries
    write_json(target_file, payload)
    return {
        "success": True,
        "data": {
            "object_id": obj["object_id"],
            "written_file": target_file.as_posix(),
            "snapshot": {hook_key: obj["body"]},
        },
    }
