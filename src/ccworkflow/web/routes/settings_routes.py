from fastapi import APIRouter

from ccworkflow.services.root_migration_service import migrate_root
from ccworkflow.services.settings_query_service import get_settings
from ccworkflow.services.settings_update_service import update_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def api_get_settings() -> dict:
    return get_settings({})


@router.put("")
def api_update_settings(payload: dict) -> dict:
    return update_settings(payload)


@router.post("/migrate-root")
def api_migrate_root(payload: dict) -> dict:
    return migrate_root(payload)
