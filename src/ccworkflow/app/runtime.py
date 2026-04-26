from pathlib import Path

from ccworkflow.repositories.settings_repository import load_settings

DEFAULT_COLLECTION_ROOT = Path("D:/Programming_tools/.ccworkflow")
ACTIVE_COLLECTION_ROOT = DEFAULT_COLLECTION_ROOT


def set_active_collection_root(path: str | Path) -> None:
    global ACTIVE_COLLECTION_ROOT
    ACTIVE_COLLECTION_ROOT = Path(path)


def get_settings_path() -> Path:
    candidate = ACTIVE_COLLECTION_ROOT / "system" / "settings.json"
    if candidate.exists():
        return candidate
    return DEFAULT_COLLECTION_ROOT / "system" / "settings.json"


def get_collection_root() -> Path:
    settings_path = get_settings_path()
    settings = load_settings({"settings_path": str(settings_path)})["data"]["settings"]
    root = Path(settings["collection_root"])
    set_active_collection_root(root)
    return root
