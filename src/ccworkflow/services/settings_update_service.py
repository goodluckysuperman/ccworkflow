from ccworkflow.app.runtime import DEFAULT_COLLECTION_ROOT, get_settings_path
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.settings_schema import SettingsDraft
from ccworkflow.repositories.settings_repository import load_settings, save_settings
from ccworkflow.services.root_init_service import ensure_root_ready


def update_settings(input_data: dict) -> dict:
    ensure_root_ready({"default_root": str(DEFAULT_COLLECTION_ROOT)})
    current = load_settings({"settings_path": str(get_settings_path())})["data"]["settings"]
    updated = SettingsDraft.model_validate(
        {
            "collection_root": current["collection_root"],
            "last_generate_mode": input_data.get("last_generate_mode", current.get("last_generate_mode", "form")),
            "last_install_scope": input_data.get("last_install_scope", current.get("last_install_scope", "project")),
            "last_filters": input_data.get("last_filters", current.get("last_filters", {})),
        }
    )
    save_settings({"settings_path": str(get_settings_path()), "settings": updated.model_dump(mode="json")})
    return AppResult(success=True, data={"updated": True, "settings": updated.model_dump(mode="json")}).model_dump()
