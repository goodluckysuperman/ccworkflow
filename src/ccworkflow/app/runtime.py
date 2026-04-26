from pathlib import Path

from ccworkflow.repositories.settings_repository import load_settings

DEFAULT_COLLECTION_ROOT = Path("D:/Programming_tools/.ccworkflow")


def get_settings_path() -> Path:
    return DEFAULT_COLLECTION_ROOT / "system" / "settings.json"


def get_collection_root() -> Path:
    settings = load_settings({"settings_path": str(get_settings_path())})["data"]["settings"]
    return Path(settings["collection_root"])
