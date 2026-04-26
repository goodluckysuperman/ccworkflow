from ccworkflow.app.runtime import DEFAULT_COLLECTION_ROOT, get_settings_path
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.settings_repository import load_settings
from ccworkflow.services.root_init_service import ensure_root_ready


def get_settings(input_data: dict | None = None) -> dict:
    ensure_root_ready({"default_root": str(DEFAULT_COLLECTION_ROOT)})
    settings = load_settings({"settings_path": str(get_settings_path())})["data"]["settings"]
    return AppResult(success=True, data=settings).model_dump()
