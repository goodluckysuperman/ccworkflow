from pathlib import Path

from ccworkflow.infra.fs_gateway import ensure_dir
from ccworkflow.infra.json_gateway import read_json, write_json


def install_mcp(input_data: dict) -> dict:
    obj = input_data["object"]
    target_file = Path(input_data["target_file"])
    resolution = input_data["resolution"]
    if resolution == "skip":
        return {"success": True, "data": {"object_id": obj["object_id"], "skipped": True, "written_file": None, "snapshot": None}}
    if resolution == "cancel":
        return {"success": False, "message": "安装已取消", "data": {"object_id": obj["object_id"]}}

    ensure_dir(target_file.parent)
    payload = read_json(target_file) if target_file.exists() else {}
    mcp_servers = payload.get("mcpServers", {}) if isinstance(payload, dict) else {}
    server_name = obj.get("extra", {}).get("server_name") or obj["name"]
    mcp_servers[server_name] = obj["body"]
    payload["mcpServers"] = mcp_servers
    write_json(target_file, payload)
    return {
        "success": True,
        "data": {
            "object_id": obj["object_id"],
            "written_file": target_file.as_posix(),
            "snapshot": {server_name: obj["body"]},
        },
    }
