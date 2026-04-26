from pathlib import Path

from ccworkflow.domain.common_schema import AppError, AppResult
from ccworkflow.domain.settings_schema import SettingsDraft
from ccworkflow.infra.fs_gateway import ensure_dir
from ccworkflow.repositories.settings_repository import load_settings, save_settings

REQUIRED_SUBDIRS = ["skills", "hooks", "mcp", "mixed", "install_records", "system", "trash"]


def ensure_root_ready(input_data: dict) -> dict:
    default_root = Path(input_data["default_root"])

    created_paths: list[str] = []
    ensure_dir(default_root)
    for name in REQUIRED_SUBDIRS:
        target = default_root / name
        if not target.exists():
            ensure_dir(target)
            created_paths.append(str(target))

    settings_path = default_root / "system" / "settings.json"
    if settings_path.exists():
        settings = load_settings({"settings_path": str(settings_path)})["data"]["settings"]
        collection_root = settings["collection_root"]
    else:
        settings = SettingsDraft(collection_root=str(default_root))
        save_settings({"settings_path": str(settings_path), "settings": settings.model_dump()})
        created_paths.append(str(settings_path))
        collection_root = str(default_root)

    return AppResult(
        success=True,
        data={
            "collection_root": collection_root,
            "created_paths": created_paths,
        },
    ).model_dump()
