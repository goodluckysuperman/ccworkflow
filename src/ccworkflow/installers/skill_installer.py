from pathlib import Path

from ccworkflow.infra.fs_gateway import ensure_dir, write_text


def install_skill(input_data: dict) -> dict:
    obj = input_data["object"]
    target_file = Path(input_data["target_file"])
    resolution = input_data["resolution"]
    if resolution == "skip":
        return {"success": True, "data": {"object_id": obj["object_id"], "skipped": True, "written_file": None, "snapshot": None}}
    if resolution == "cancel":
        return {"success": False, "message": "安装已取消", "data": {"object_id": obj["object_id"]}}

    ensure_dir(target_file.parent)
    write_text(target_file, obj["body"])
    return {
        "success": True,
        "data": {
            "object_id": obj["object_id"],
            "written_file": target_file.as_posix(),
            "snapshot": obj["body"],
        },
    }
