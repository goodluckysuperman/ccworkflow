import shutil
from pathlib import Path

from ccworkflow.app.runtime import DEFAULT_COLLECTION_ROOT, get_collection_root, get_settings_path
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.infra.path_policy import validate_collection_root
from ccworkflow.repositories.settings_repository import load_settings, save_settings
from ccworkflow.services.root_init_service import ensure_root_ready


def migrate_root(input_data: dict) -> dict:
    ensure_root_ready({"default_root": str(DEFAULT_COLLECTION_ROOT)})
    new_root = Path(input_data["new_root"])
    current_root = get_collection_root()

    validation = validate_collection_root({"collection_root": str(new_root)})
    if not validation["success"]:
        return validation
    if new_root.resolve() == current_root.resolve():
        return AppResult(success=True, data={"old_root": current_root.as_posix(), "new_root": new_root.as_posix(), "migrated": False}).model_dump()

    temp_root = new_root.parent / f"{new_root.name}.tmp"
    if temp_root.exists():
        shutil.rmtree(temp_root)

    shutil.copytree(current_root, temp_root)
    temp_settings_path = temp_root / "system" / "settings.json"
    temp_settings = load_settings({"settings_path": str(temp_settings_path)})["data"]["settings"]
    temp_settings["collection_root"] = new_root.as_posix()
    save_settings({"settings_path": str(temp_settings_path), "settings": temp_settings})

    if new_root.exists():
        shutil.rmtree(new_root)
    temp_root.rename(new_root)

    active_settings = load_settings({"settings_path": str(new_root / "system" / "settings.json")})["data"]["settings"]
    active_settings["collection_root"] = new_root.as_posix()
    save_settings({"settings_path": str(new_root / "system" / "settings.json"), "settings": active_settings})

    return AppResult(success=True, data={"old_root": current_root.as_posix(), "new_root": new_root.as_posix(), "migrated": True}).model_dump()
