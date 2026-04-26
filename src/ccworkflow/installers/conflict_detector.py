import json
from pathlib import Path
from typing import Any

from ccworkflow.domain.common_schema import AppResult


def detect_conflicts(input_data: dict) -> dict:
    targets = input_data.get("targets", [])
    objects = input_data.get("objects", [])
    object_map = {obj["object_id"]: obj for obj in objects}
    conflicts: list[dict[str, Any]] = []

    for target in targets:
        object_id = target["object_id"]
        obj = object_map[object_id]
        target_file = Path(target["target_file"])

        if target["target_kind"] == "skill_file":
            if target_file.exists():
                conflicts.append(
                    {
                        "object_id": object_id,
                        "type": obj["type"],
                        "object_name": obj["name"],
                        "target_file": str(target_file),
                        "conflict_key": obj["name"],
                        "reason": "same_name",
                    }
                )
            continue

        if not target_file.exists():
            continue

        if target["target_kind"] == "settings_json":
            payload = _safe_load_json(target_file)
            hook_key = obj.get("extra", {}).get("hook_key", "")
            if hook_key and hook_key in json.dumps(payload, ensure_ascii=False):
                conflicts.append(
                    {
                        "object_id": object_id,
                        "type": obj["type"],
                        "object_name": obj["name"],
                        "target_file": str(target_file),
                        "conflict_key": hook_key,
                        "reason": "same_key",
                    }
                )
            continue

        if target["target_kind"] == "mcp_json":
            payload = _safe_load_json(target_file)
            server_name = obj.get("extra", {}).get("server_name", "")
            mcp_servers = payload.get("mcpServers", {}) if isinstance(payload, dict) else {}
            if server_name and server_name in mcp_servers:
                conflicts.append(
                    {
                        "object_id": object_id,
                        "type": obj["type"],
                        "object_name": obj["name"],
                        "target_file": str(target_file),
                        "conflict_key": server_name,
                        "reason": "same_server_name",
                    }
                )

    return AppResult(success=True, data={"conflicts": conflicts}).model_dump()


def _safe_load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
